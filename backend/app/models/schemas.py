from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# Authentication Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class TokenData(BaseModel):
    email: Optional[str] = None

# User Schema
class User(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    agent_persona: str = "strict_formal"
    created_at: datetime
    is_active: bool = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    agent_persona: Optional[str] = None

# Update existing QueryRequest to include user_id
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    session_id: str
    data: 'ComplianceAssessment'

# Keep existing ComplianceAssessment and ComplianceSource
class ComplianceSource(BaseModel):
    document_name: str
    excerpt: str
    relevance_score: float

class ComplianceAssessment(BaseModel):
    response: str
    status: Optional[str] = None
    reasoning: Optional[str] = None
    relevant_clauses: List[str] = []
    sources: List[ComplianceSource] = []
    conversation_type: str = "analysis"
    follow_up_questions: List[str] = []
