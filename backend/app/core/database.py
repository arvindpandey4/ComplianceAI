import os
from motor.motor_asyncio import AsyncIOMotorClient

class Database:
    client: AsyncIOMotorClient = None
    db = None

    def connect(self):
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client["compliance_rag_db"]
        print("Connected to MongoDB.")

    def close(self):
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB.")

db = Database()
