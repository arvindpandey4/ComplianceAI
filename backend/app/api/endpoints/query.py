from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import uuid

# use new PydanticAI agent
from app.services.pydantic_agent import run_pydantic_agent
from app.services.vector_store import VectorStoreService
from app.services.chat_history import ChatHistoryService
from app.models.schemas import QueryRequest, QueryResponse

router = APIRouter()

def get_vector_store():
    return VectorStoreService()

def get_chat_service():
    return ChatHistoryService()

@router.post("/")
async def query_compliance(
    request: QueryRequest,
    vector_store: VectorStoreService = Depends(get_vector_store),
    chat_service: ChatHistoryService = Depends(get_chat_service)
):
    print(f"[QUERY] Processing: {request.query}")
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        # Run PydanticAI Agent
        # The agent handles tool orchestration (context retrieval, history, etc.)
        result_data = await run_pydantic_agent(request.query, session_id=session_id)
        
        print(f"[QUERY] Completed. Status: {result_data.status}")
        
        # Save Interaction to DB
        # We save separate messages for user and assistant
        await chat_service.add_message(session_id, "user", request.query)
        
        # Ensure we always have a string response
        response_text = result_data.response
        if not response_text and result_data.reasoning:
            response_text = result_data.reasoning
        if not response_text:
            response_text = "Analysis completed."
            
        await chat_service.add_message(session_id, "assistant", response_text)
        
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

