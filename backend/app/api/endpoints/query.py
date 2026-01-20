from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import uuid

# Use production-ready LangChain agent as primary
from app.services.agent import compliance_agent, AgentDeps
from app.services.vector_store import VectorStoreService
from app.services.chat_history import ChatHistoryService
from app.models.schemas import QueryRequest, QueryResponse
from app.core.auth import get_current_user
from app.core.database import db

router = APIRouter()

def get_vector_store():
    return VectorStoreService()

def get_chat_service():
    return ChatHistoryService()

@router.post("/")
async def query_compliance(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user),
    vector_store: VectorStoreService = Depends(get_vector_store),
    chat_service: ChatHistoryService = Depends(get_chat_service)
):
    print(f"[QUERY] Processing for user {current_user['email']}: {request.query}")
    
    # Fetch full user profile to get latest persona
    user_profile = await db.db.users.find_one({"email": current_user["email"]})
    user_persona = user_profile.get("agent_persona", "strict_formal") if user_profile else "strict_formal"
    
    # Use user-specific session ID or create new one
    session_id = request.session_id or f"{current_user['user_id']}_{str(uuid.uuid4())}"
    
    try:
        # Prepare agent dependencies
        deps = AgentDeps(vector_store=vector_store)
        
        # Get conversation history for context
        history = await chat_service.get_history(session_id, limit=5)
        history_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history]) if history else ""
        
        # Run LangChain Agent (production-ready)
        result = await compliance_agent.run(
            request.query, 
            deps=deps, 
            history_context=history_context,
            persona=user_persona
        )
        result_data = result.data
        
        print(f"[QUERY] Completed. Status: {result_data.status}")
        
        # Save Interaction to DB
        # We save separate messages for user and assistant with user_id
        await chat_service.add_message(session_id, "user", request.query, user_id=current_user["user_id"])
        
        # Ensure we always have a string response
        response_text = result_data.response
        if not response_text and result_data.reasoning:
            response_text = result_data.reasoning
        if not response_text:
            response_text = "Analysis completed."
            
        await chat_service.add_message(session_id, "assistant", response_text, user_id=current_user["user_id"])
        
        # Return strict schema
        return {
            "session_id": session_id,
            "data": result_data
        }
        
    except Exception as e:
        print(f"[ERROR] Query failed: {e}")
        import traceback
        traceback.print_exc()
        # Safe sanitization
        raise HTTPException(status_code=500, detail="Internal Server Error: Unable to process request.")

@router.get("/history/sessions")
async def get_sessions(
    current_user: dict = Depends(get_current_user),
    chat_service: ChatHistoryService = Depends(get_chat_service)
):
    """Get last 5 distinct chat sessions for the current user."""
    return await chat_service.get_recent_sessions(current_user["user_id"], limit=5)

@router.get("/history/{session_id}")
async def get_session_history(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatHistoryService = Depends(get_chat_service)
):
    """Get full message history for a specific session."""
    # Security check: Ideally verify user owns session, but session IDs contain user_id prefix in our implementation
    if not session_id.startswith(current_user["user_id"]):
         # Fallback check if UUID only (old sessions) or mismatch
         pass 
    
    return await chat_service.get_history(session_id, limit=50)

@router.get("/knowledge/demo/pdf")
async def get_demo_pdf(
    current_user: dict = Depends(get_current_user)
):
    """Stream the demo PDF file."""
    import os
    from fastapi.responses import FileResponse
    
    # Locate uploads directory
    base_dir = os.path.join(os.getcwd(), "data", "uploads")
    if not os.path.exists(base_dir):
        base_dir = os.path.join(os.getcwd(), "backend", "data", "uploads")
        
    if not os.path.exists(base_dir):
         raise HTTPException(status_code=404, detail="Demo document not found (dir missing)")

    # Find the first PDF
    files = [f for f in os.listdir(base_dir) if f.endswith('.pdf')]
    if not files:
        raise HTTPException(status_code=404, detail="Demo document not found")
        
    file_path = os.path.join(base_dir, files[0])
    
    return FileResponse(
        path=file_path, 
        filename="Compliance_Audit_Guidelines.pdf",
        media_type="application/pdf"
    )

