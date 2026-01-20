from app.core.database import db
from typing import List, Dict
from datetime import datetime

class ChatHistoryService:
    def __init__(self):
        self.collection = db.db["chat_history"]

    async def add_message(self, session_id: str, role: str, content: str, user_id: str = None):
        message = {
            "session_id": session_id,
            "user_id": user_id,
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

    async def get_recent_sessions(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Get the last N active sessions for a user."""
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$sort": {"timestamp": -1}},
            {"$group": {
                "_id": "$session_id",
                "last_message": {"$first": "$content"},
                "timestamp": {"$first": "$timestamp"}
            }},
            {"$sort": {"timestamp": -1}},
            {"$limit": limit}
        ]
        cursor = self.collection.aggregate(pipeline)
        sessions = await cursor.to_list(length=limit)
        return [{"session_id": s["_id"], "preview": s["last_message"][:50] + "...", "timestamp": s["timestamp"]} for s in sessions]
