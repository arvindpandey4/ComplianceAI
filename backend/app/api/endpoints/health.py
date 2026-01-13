from fastapi import APIRouter
from app.core.database import db
import os

router = APIRouter()

@router.get("/")
async def health_check():
    mongo_status = "Connected" if db.client else "Disconnected"
    return {
        "status": "active",
        "environment": os.getenv("PROJECT_NAME", "Unknown"),
        "database_status": mongo_status
    }
