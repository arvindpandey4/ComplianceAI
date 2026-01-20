import os
from motor.motor_asyncio import AsyncIOMotorClient

class Database:
    client: AsyncIOMotorClient = None
    db = None

    async def connect(self):
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        
        # MongoDB Atlas requires specific connection options
        connection_options = {
            "retryWrites": True,
            "w": "majority",
            "serverSelectionTimeoutMS": 5000,
            "connectTimeoutMS": 10000,
        }
        
        try:
            self.client = AsyncIOMotorClient(mongo_uri, **connection_options)
            self.db = self.client["compliance_rag_db"]
            
            # Create indexes
            await self.db.users.create_index("email", unique=True)
            await self.db.chat_history.create_index("user_id")
            await self.db.chat_history.create_index("session_id")
            
            # Determine connection type for logging
            connection_type = "MongoDB Atlas" if "mongodb+srv://" in mongo_uri else "Local MongoDB"
            print(f"✓ Connected to {connection_type}")
        except Exception as e:
            print(f"✗ Failed to connect to MongoDB: {e}")
            raise

    def close(self):
        if self.client:
            self.client.close()
            print("✓ Disconnected from MongoDB")

db = Database()
