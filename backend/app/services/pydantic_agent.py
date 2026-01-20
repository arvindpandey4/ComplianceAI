import os
import logging
import re
from typing import Optional
from dotenv import load_dotenv

from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.models.openai import OpenAIModel

from app.models.schemas import ComplianceAssessment, ComplianceSource
from app.services.vector_store import VectorStoreService
from app.services.chat_history import ChatHistoryService
from app.services.followup_service import followup_service

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger("pydantic_agent")
logger.setLevel(logging.INFO)

# ------------------------------------------------------------------
# Model Configuration
# ------------------------------------------------------------------

def get_primary_model():
    """Returns the primary Groq model."""
    return GroqModel('llama-3.3-70b-versatile')

def get_fallback_model():
    """Returns the fallback OpenRouter model."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.warning("OPENROUTER_API_KEY not found.")
        return None
    
    # Set environment variables for OpenAI-compatible client
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"
    
    return OpenAIModel('meta-llama/llama-3.3-70b-instruct:free')

# ------------------------------------------------------------------
# System Prompt (No Tool Calling - Prompt-Based)
# ------------------------------------------------------------------

system_prompt = """You are an expert Regulatory Compliance Assistant. Provide clear, actionable guidance.

CRITICAL: You MUST return a valid JSON object with these exact fields:

{
  "response": "2-4 sentence concise answer here",
  "status": "Compliant" or "Non-Compliant" or "Needs Review" or null,
  "reasoning": "Detailed technical analysis here" or null,
  "relevant_clauses": ["clause 1", "clause 2"] or [],
  "sources": [],
  "conversation_type": "analysis" or "follow_up" or "clarification",
  "follow_up_questions": []
}

RESPONSE FIELD (REQUIRED):
- Keep it 2-4 sentences maximum
- Direct, conversational answer
- Example: "Yes, your policy complies with GDPR Article 5(1)(e). It correctly implements data retention limits."

REASONING FIELD (optional):
- Comprehensive technical breakdown
- Specific clause references

CONVERSATION_TYPE:
- "analysis" = new compliance question
- "follow_up" = "tell me more"
- "clarification" = "what does X mean?"

IMPORTANT: The 'response' field is MANDATORY. Base your answer STRICTLY on the provided context."""

# ------------------------------------------------------------------
# Agent Definition (NO TOOLS - Simplified)
# ------------------------------------------------------------------

compliance_agent = Agent(
    model=get_primary_model(),
    result_type=ComplianceAssessment,
    system_prompt=system_prompt,
    retries=1
)

# ------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------

def _add_followup_questions(result: ComplianceAssessment, docs: list) -> ComplianceAssessment:
    """Add follow-up questions based on retrieved documents."""
    if result.follow_up_questions and len(result.follow_up_questions) > 0:
        return result
    
    # Try to find KB entry IDs
    kb_ids = [doc.metadata.get("id") for doc in docs if doc.metadata.get("type") == "kb_entry"]
    
    if kb_ids:
        result.follow_up_questions = followup_service.get_followup_questions(kb_ids[0], max_questions=3)
    else:
        result.follow_up_questions = followup_service.get_followup_questions(None, max_questions=2)
    
    return result

# ------------------------------------------------------------------
# Main Orchestration Logic
# ------------------------------------------------------------------

async def run_pydantic_agent(query: str, session_id: str = "default") -> ComplianceAssessment:
    """
    Main entry point for the PydanticAI Agent.
    Uses a simplified prompt-based approach instead of tool calling.
    """
    
    # Initialize services
    vs_service = VectorStoreService()
    
    # Retrieve relevant documents
    docs = vs_service.search(query, k=5)
    
    # FAST PATH: Check if top result is a Golden KB entry
    if docs and len(docs) > 0:
        top_doc = docs[0]
        is_kb_entry = top_doc.metadata.get("type") == "kb_entry"
        
        if is_kb_entry:
            # Extract the structured content from the KB entry
            content = top_doc.page_content
            content_match = re.search(r'CONTENT:\s*(.+?)(?=\n\n[A-Z_]+:|$)', content, re.DOTALL)
            
            if content_match:
                direct_answer = content_match.group(1).strip()
                kb_id = top_doc.metadata.get("id", "Unknown")
                kb_title = top_doc.metadata.get("title", "Knowledge Base Entry")
                
                # Get follow-up questions for this KB entry
                followup_questions = followup_service.get_followup_questions(kb_id, max_questions=3)
                
                logger.info(f"[FAST PATH] Returning direct KB answer from {kb_id}")
                
                # Return structured response without LLM call
                return ComplianceAssessment(
                    response=direct_answer,
                    status=None,
                    reasoning=f"Source: {kb_title} ({kb_id})",
                    relevant_clauses=[],
                    sources=[ComplianceSource(
                        document_name=kb_title,
                        excerpt=direct_answer[:200] + "..." if len(direct_answer) > 200 else direct_answer,
                        relevance_score=1.0
                    )],
                    conversation_type="kb_direct",
                    follow_up_questions=followup_questions
                )
    
    # STANDARD PATH: Build context and call LLM
    context_str = "\n\n".join([
        f"Document: {doc.metadata.get('title', 'Unknown')}\n{doc.page_content}" 
        for doc in docs
    ])
    
    if not context_str.strip():
        context_str = "No specific regulatory documents were found."
    
    # Build the user prompt with context
    user_prompt = f"""Regulatory Context:
{context_str}

Current Query: {query}

Return ONLY valid JSON matching the schema provided in the system prompt."""
    
    # Execute with Primary Model (Groq)
    try:
        logger.info(f"[PRIMARY] Running Groq agent for query: {query[:50]}...")
        result = await compliance_agent.run(user_prompt)
        assessment = result.data
        
        # Add follow-up questions
        assessment = _add_followup_questions(assessment, docs)
        
        logger.info(f"[PRIMARY] Success - Status: {assessment.status}")
        return assessment
        
    except Exception as e:
        logger.error(f"Primary Agent failed: {e}. Attempting Fallback.")
        
        # FALLBACK LOGIC
        fallback_model = get_fallback_model()
        if not fallback_model:
            logger.error("Fallback model not available (missing OPENROUTER_API_KEY)")
            return ComplianceAssessment(
                response="I apologize, but I am currently unable to process your request. Please try again later.",
                status="Needs Review",
                reasoning=f"System Error: {str(e)}",
                conversation_type="error"
            )
        
        try:
            logger.info("[FALLBACK] Running OpenRouter agent...")
            
            # Create fallback agent
            fallback_agent = Agent(
                model=fallback_model,
                result_type=ComplianceAssessment,
                system_prompt=system_prompt,
                retries=1
            )
            
            result = await fallback_agent.run(user_prompt)
            assessment = result.data
            
            # Add follow-up questions
            assessment = _add_followup_questions(assessment, docs)
            
            logger.info(f"[FALLBACK] Success - Status: {assessment.status}")
            return assessment
            
        except Exception as fallback_e:
            logger.error(f"Fallback Agent also failed: {fallback_e}")
            
            # Safe Error Return
            return ComplianceAssessment(
                response="I apologize, but I am currently unable to process your request due to technical difficulties. Please try again in a moment.",
                status="Needs Review",
                reasoning=f"Primary Error: {str(e)} | Fallback Error: {str(fallback_e)}",
                conversation_type="error"
            )
