from pydantic import BaseModel, Field
from typing import List, Optional

class ComplianceSource(BaseModel):
    document_name: str
    excerpt: str
    relevance_score: Optional[float] = None

class ComplianceAssessment(BaseModel):
    response: Optional[str] = Field(default=None, description="Natural, conversational response to the user's query")
    status: Optional[str] = Field(default=None, description="Compliant, Non-Compliant, Needs Review, or N/A for follow-up questions")
    reasoning: Optional[str] = Field(default=None, description="Detailed technical explanation when needed")
    relevant_clauses: List[str] = Field(default_factory=list, description="Specific clauses or rules found")
    sources: List[ComplianceSource] = Field(default_factory=list, description="Source documents referenced")
    conversation_type: str = Field(default="analysis", description="Type: 'analysis', 'follow_up', 'clarification', or 'expansion'")

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    session_id: str
    data: ComplianceAssessment
