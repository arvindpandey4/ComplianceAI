from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from app.services.agent import compliance_agent, AgentDeps
from app.services.vector_store import VectorStoreService
from app.services.chat_history import ChatHistoryService
from app.models.schemas import QueryRequest, QueryResponse
import uuid

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
        # Retrieve conversation history
        history = await chat_service.get_history(session_id)
        
        # Format history for better context
        formatted_history = ""
        if history:
            formatted_history = "\n".join([
                f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}" 
                for msg in history
            ])
        
        deps = AgentDeps(vector_store=vector_store)
        
        result = await compliance_agent.run(
            query=request.query, 
            deps=deps, 
            history_context=formatted_history
        )
        print(f"[QUERY] Completed. Status: {result.data.status}")
        
        # Save user message
        await chat_service.add_message(session_id, "user", request.query)
        
        # Save the conversational response (fallback to reasoning if empty)
        response_to_save = result.data.response or result.data.reasoning or "Processed."
        result.data.response = response_to_save
        
        await chat_service.add_message(session_id, "assistant", response_to_save)
        
        return {
            "session_id": session_id,
            "data": result.data
        }
        
    except Exception as e:
        print(f"[ERROR] Query failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

