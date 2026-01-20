import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def test_mongo():
    uri = os.getenv("MONGODB_URI")
    print(f"Testing connection to: {uri.split('@')[-1]}") # Hiding credentials
    
    try:
        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
        # Force a connection verification
        await client.admin.command('ping')
        print("✅ SUCCESS: Successfully connected to MongoDB Atlas!")
    except Exception as e:
        print(f"❌ FAIL: Connection failed.\nError: {e}")

if __name__ == "__main__":
    asyncio.run(test_mongo())
