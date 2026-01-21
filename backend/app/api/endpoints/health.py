from fastapi import APIRouter, HTTPException
from app.core.database import db
import os
from datetime import datetime

router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    mongo_status = "Connected" if db.client else "Disconnected"
    return {
        "status": "active",
        "environment": os.getenv("PROJECT_NAME", "Unknown"),
        "database_status": mongo_status
    }

@router.get("/status")
async def detailed_health_check():
    """
    Detailed health check endpoint for frontend to verify backend is ready.
    This endpoint is specifically designed to handle cold starts on Render.
    """
    try:
        # Check database connectivity
        mongo_connected = False
        if db.client:
            try:
                # Ping the database to ensure it's actually connected
                await db.client.admin.command('ping')
                mongo_connected = True
            except Exception as e:
                print(f"MongoDB ping failed: {e}")
                mongo_connected = False
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "connected": mongo_connected,
                "status": "operational" if mongo_connected else "unavailable"
            },
            "service": {
                "name": "ComplianceAI Backend",
                "version": "1.0.0",
                "environment": os.getenv("ENVIRONMENT", "production")
            },
            "message": "Backend is ready to accept requests"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service temporarily unavailable: {str(e)}"
        )

