from app.core.database import db
from typing import List, Dict
from datetime import datetime

class ChatHistoryService:
    def __init__(self):
        self.collection = db.db["chat_history"]

    async def add_message(self, session_id: str, role: str, content: str):
        message = {
            "session_id": session_id,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow()
        }
        await self.collection.insert_one(message)

    async def get_history(self, session_id: str, limit: int = 20) -> List[Dict]:
        """Retrieve conversation history with increased context window"""
        cursor = self.collection.find({"session_id": session_id}).sort("timestamp", 1).limit(limit)
        history = await cursor.to_list(length=limit)
        return [{"role": msg["role"], "content": msg["content"]} for msg in history]
