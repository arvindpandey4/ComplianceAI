import time
import uuid
from fastapi import Request
from loguru import logger

async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    
    # Log Request
    logger.info(f"[{correlation_id}] Incoming Request: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add Header to response for tracing
        response.headers["X-Correlation-ID"] = correlation_id
        
        # Log Response
        logger.info(
            f"[{correlation_id}] Response: {response.status_code} "
            f"Process Time: {process_time:.4f}s"
        )
        return response
        
    except Exception as e:
        logger.error(f"[{correlation_id}] Request Failed: {str(e)}")
        raise e
