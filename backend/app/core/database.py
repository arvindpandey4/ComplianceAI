import os
from motor.motor_asyncio import AsyncIOMotorClient

class Database:
    client: AsyncIOMotorClient = None
    db = None

    async def connect(self):
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        
        # Optimized MongoDB connection options for production (Render + Atlas)
        connection_options = {
            "retryWrites": True,
            "w": "majority",
            # Increased timeouts for cold starts
            "serverSelectionTimeoutMS": 30000,  # 30 seconds
            "connectTimeoutMS": 30000,  # 30 seconds
            "socketTimeoutMS": 45000,  # 45 seconds
            # Connection pooling for better performance
            "maxPoolSize": 50,
            "minPoolSize": 10,
            # Keep connections alive
            "maxIdleTimeMS": 45000,
        }
        
        try:
            print("🔄 Connecting to MongoDB...")
            self.client = AsyncIOMotorClient(mongo_uri, **connection_options)
            self.db = self.client["compliance_rag_db"]
            
            # Verify connection with ping
            await self.client.admin.command('ping')
            
            # Create indexes (with background=True for non-blocking)
            await self.db.users.create_index("email", unique=True, background=True)
            await self.db.chat_history.create_index("user_id", background=True)
            await self.db.chat_history.create_index("session_id", background=True)
            
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
