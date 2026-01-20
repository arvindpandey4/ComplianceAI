from dotenv import load_dotenv

load_dotenv()

from typing import List, Optional
from pydantic import BaseModel, Field

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.services.vector_store import VectorStoreService
from app.models.schemas import ComplianceAssessment, ComplianceSource
from app.services.followup_service import followup_service
from app.core.token_manager import token_manager
import os
import logging

# Configure logging
logger = logging.getLogger("compliance_agent")
logger.setLevel(logging.INFO)

class AgentDeps:
    """Agent dependencies for dependency injection."""
    def __init__(self, vector_store: VectorStoreService):
        self.vector_store = vector_store

class ComplianceAgent:
    """
    Production-ready LangChain-based Compliance Agent.
    Provides fast-path KB retrieval and robust LLM fallback.
    """
    
    def __init__(self):
        """Initialize the agent with Groq LLM and output parser."""
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.3,
            max_retries=2
        )
        
        self.parser = PydanticOutputParser(pydantic_object=ComplianceAssessment)
        
        # Production-optimized prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Regulatory Compliance Assistant.
{persona_instruction}

CRITICAL: You MUST return a valid JSON object with these exact fields:

{{
  "response": "2-4 sentence concise answer here (adjust tone based on persona)",
  "status": "Compliant" or "Non-Compliant" or "Needs Review" or null,
  "reasoning": "Detailed technical analysis here" or null,
  "relevant_clauses": ["clause 1", "clause 2"] or [],
  "sources": [],
  "conversation_type": "analysis" or "follow_up" or "clarification" or "expansion",
  "follow_up_questions": []
}}

RESPONSE FIELD (REQUIRED):
- Keep it 2-4 sentences maximum
- Direct, conversational answer
- Example: "Yes, your policy complies with GDPR Article 5(1)(e). It correctly implements data retention limits and includes proper deletion procedures."

IMPORTANT: 
- The 'response' field is MANDATORY and must contain a concise answer.
- If regulatory context is provided, base your answer STRICTLY on it.
- If no relevant context is found, you may answer based on your general knowledge but clearly state that this is general advice not based on uploaded documents."""),
            ("user", """Previous Conversation:
{history_context}

Regulatory Context:
{context}

Current Query: {query}

Return ONLY valid JSON. Put the concise answer in 'response' field (REQUIRED), detailed analysis in 'reasoning' field (optional).

{format_instructions}""")
        ])
        
        self.chain = self.prompt | self.llm | self.parser
        
        logger.info("ComplianceAgent initialized successfully")

    def _extract_json_from_markdown(self, text: str) -> str:
        """Extract JSON from markdown code blocks if present."""
        import re
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, text, re.DOTALL)
        return match.group(1) if match else text
    
    def _add_followup_questions(self, result: ComplianceAssessment, docs: list) -> ComplianceAssessment:
        """
        Enrich the response with follow-up questions based on retrieved documents.
        
        Args:
            result: The ComplianceAssessment result from the LLM
            docs: List of retrieved documents
            
        Returns:
            Enhanced ComplianceAssessment with follow-up questions
        """
        # If result already has follow-up questions, don't override
        if result.follow_up_questions and len(result.follow_up_questions) > 0:
            return result
        
        # Try to find KB entry IDs from the retrieved documents
        kb_ids = []
        for doc in docs:
            if doc.metadata.get("type") == "kb_entry":
                kb_id = doc.metadata.get("id")
                if kb_id:
                    kb_ids.append(kb_id)
        
        # Get follow-up questions for the first KB entry found
        if kb_ids:
            followup_questions = followup_service.get_followup_questions(kb_ids[0], max_questions=3)
            result.follow_up_questions = followup_questions
        else:
            # Use general follow-up questions if no KB entry found
            general_questions = followup_service.get_followup_questions(None, max_questions=2)
            result.follow_up_questions = general_questions
        
        return result

    async def run(self, query: str, deps: AgentDeps, history_context: str = "", persona: str = "strict_formal"):
        """
        Execute the compliance agent with the given query.
        
        Args:
            query: User's compliance question
            deps: Agent dependencies (vector store, etc.)
            history_context: Previous conversation context
            persona: Agent persona (strict_formal, educational, risk_focused, concise)
            
        Returns:
            Object with 'data' attribute containing ComplianceAssessment
        """
        logger.info(f"[QUERY] Processing: {query[:100]}... Persona: {persona}")
        
        # Persona Logic
        persona_map = {
            "strict_formal": "Adopt a formal, authoritative tone. Focus strictly on regulatory text compliance.",
            "educational": "Adopt a helpful, teaching tone. Explain the 'why' behind regulations. Be patient and clear.",
            "risk_focused": "Prioritize risk assessment. Highlight potential penalties, gaps, and worst-case scenarios first.",
            "concise": "Be extremely brief and to the point. Use bullet points. Avoid all unnecessary words."
        }
        persona_instruction = persona_map.get(persona, persona_map["strict_formal"])
        
        # Retrieve relevant documents
        docs = deps.vector_store.search(query, k=5)
        
        # FAST PATH: Check if top result is a Golden KB entry
        # If so, return direct answer without LLM processing
        if docs and len(docs) > 0:
            top_doc = docs[0]
            is_kb_entry = top_doc.metadata.get("type") == "kb_entry"
            
            if is_kb_entry:
                # Extract the structured content from the KB entry
                content = top_doc.page_content
                
                # Parse out the CONTENT section (the actual answer)
                import re
                content_match = re.search(r'CONTENT:\s*(.+?)(?=\n\n[A-Z_]+:|$)', content, re.DOTALL)
                
                if content_match:
                    direct_answer = content_match.group(1).strip()
                    kb_id = top_doc.metadata.get("id", "Unknown")
                    kb_title = top_doc.metadata.get("title", "Knowledge Base Entry")
                    
                    # Get follow-up questions for this KB entry
                    followup_questions = followup_service.get_followup_questions(kb_id, max_questions=3)
                    
                    logger.info(f"[FAST PATH] Returning direct KB answer from {kb_id} with {len(followup_questions)} follow-up questions")
                    
                    # Return structured response without LLM call
                    return type('obj', (object,), {'data': ComplianceAssessment(
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
                    )})
        
        # STANDARD PATH: Continue with LLM processing
        context_str = "\n".join([d.page_content for d in docs])
        
        # Validate and manage token limits
        final_context = token_manager.validate_and_truncate(
            history=history_context, 
            regulatory_context=context_str, 
            query=query
        )

        if not final_context.strip():
             final_context = "No specific regulatory documents were found. Provide a helpful response based on general knowledge."

        try:
            logger.info("[STANDARD PATH] Invoking LLM chain...")
            
            # Standard execution flow
            result = await self.chain.ainvoke({
                "query": query,
                "context": final_context,
                "history_context": history_context if history_context else "Start of conversation.",
                "persona_instruction": persona_instruction,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            # Add follow-up questions to the result
            result = self._add_followup_questions(result, docs)
            
            logger.info(f"[SUCCESS] Status: {result.status}, Type: {result.conversation_type}")
            
            return type('obj', (object,), {'data': result})
            
        except Exception as e:
            logger.warning(f"[FALLBACK] Primary chain failed: {e}. Attempting JSON extraction...")
            
            # Clean single fallback layer for Markdown/JSON issues
            try:
                raw_chain = self.prompt | self.llm
                raw_res = await raw_chain.ainvoke({
                    "query": query,
                    "context": final_context,
                    "history_context": history_context,
                    "format_instructions": self.parser.get_format_instructions()
                })
                
                content = raw_res.content if hasattr(raw_res, 'content') else str(raw_res)
                cleaned_json = self._extract_json_from_markdown(content)
                
                import json
                parsed = json.loads(cleaned_json)
                
                # Create object from dict
                data = ComplianceAssessment(**parsed)
                
                # Add follow-up questions
                data = self._add_followup_questions(data, docs)
                
                logger.info(f"[FALLBACK SUCCESS] Recovered via JSON extraction")
                
                return type('obj', (object,), {'data': data})
                
            except Exception as fallback_e:
                logger.error(f"[ERROR] Both primary and fallback failed: {fallback_e}")
                import traceback
                traceback.print_exc()
                
                # Final safe return to prevent server crash
                return type('obj', (object,), {'data': ComplianceAssessment(
                    response="I apologize, but I encountered a technical issue processing your request. Please try rephrasing your question or contact support if the issue persists.",
                    status="Needs Review",
                    reasoning=f"System Error: {str(e)} | Fallback Error: {str(fallback_e)}",
                    conversation_type="error"
                )})

# Global agent instance (singleton pattern)
compliance_agent = ComplianceAgent()
