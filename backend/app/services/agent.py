from dotenv import load_dotenv

load_dotenv()

from typing import List, Optional
from pydantic import BaseModel, Field

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.services.vector_store import VectorStoreService
from app.models.schemas import ComplianceAssessment, ComplianceSource
import os

class AgentDeps:
    def __init__(self, vector_store: VectorStoreService):
        self.vector_store = vector_store

from app.core.token_manager import token_manager

class ComplianceAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.3
        )
        
        self.parser = PydanticOutputParser(pydantic_object=ComplianceAssessment)
        
        # Refined prompt for concise responses with detailed explanations
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Regulatory Compliance Assistant. Provide clear, actionable guidance.

CRITICAL: You MUST return a valid JSON object with these exact fields:

{{
  "response": "2-4 sentence concise answer here",
  "status": "Compliant" or "Non-Compliant" or "Needs Review" or null,
  "reasoning": "Detailed technical analysis here" or null,
  "relevant_clauses": ["clause 1", "clause 2"] or [],
  "sources": [],
  "conversation_type": "analysis" or "follow_up" or "clarification" or "expansion"
}}

RESPONSE FIELD (REQUIRED):
- Keep it 2-4 sentences maximum
- Direct, conversational answer
- Example: "Yes, your policy complies with GDPR Article 5(1)(e). It correctly implements data retention limits and includes proper deletion procedures."

REASONING FIELD (optional):
- Comprehensive technical breakdown
- Specific clause references
- This is shown when user clicks "Show details"

CONVERSATION_TYPE:
- "analysis" = new compliance question
- "follow_up" = "tell me more"
- "clarification" = "what does X mean?"

IMPORTANT: The 'response' field is MANDATORY and must contain a concise answer."""),
            ("user", """Previous Conversation:
{history_context}

Regulatory Context:
{context}

Current Query: {query}

Return ONLY valid JSON. Put the concise answer in 'response' field (REQUIRED), detailed analysis in 'reasoning' field (optional).

{format_instructions}""")
        ])
        
        self.chain = self.prompt | self.llm | self.parser

    def _extract_json_from_markdown(self, text: str) -> str:
        """Extract JSON from markdown code blocks if present"""
        import re
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, text, re.DOTALL)
        return match.group(1) if match else text

    async def run(self, query: str, deps: AgentDeps, history_context: str = ""):
        # Retrieve relevant documents
        docs = deps.vector_store.search(query, k=5)
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
            # Standard execution flow
            result = await self.chain.ainvoke({
                "query": query,
                "context": final_context,
                "history_context": history_context if history_context else "Start of conversation.",
                "format_instructions": self.parser.get_format_instructions()
            })
            return type('obj', (object,), {'data': result})
            
        except Exception:
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
                return type('obj', (object,), {'data': data})
                
            except Exception as e:
                print(f"Agent Error: {e}")
                import traceback
                traceback.print_exc()
                # Final safe return to prevent server crash
                return type('obj', (object,), {'data': ComplianceAssessment(
                    response=f"System Error: {str(e)}",  # Show the actual error!
                    status="Needs Review",
                    conversation_type="error"
                )})

compliance_agent = ComplianceAgent()


