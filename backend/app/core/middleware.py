import time
from fastapi import Request
from loguru import logger

async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Log Request
    logger.info(f"Incoming Request: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log Response
        logger.info(
            f"Response: {response.status_code} "
            f"Process Time: {process_time:.4f}s"
        )
        return response
        
    except Exception as e:
        logger.error(f"Request Failed: {str(e)}")
        raise e
