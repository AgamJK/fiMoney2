import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables
load_dotenv()

# MongoDB configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "fi_gemini_finance")

async def test_connection():
    """Test MongoDB connection and basic operations"""
    print("🔍 Testing MongoDB connection...")
    
    # Create a new client and connect to the server
    client = AsyncIOMotorClient(MONGODB_URL)
    
    try:
        # Check server info
        server_info = await client.server_info()
        print(f"✅ Connected to MongoDB server version {server_info['version']}")
        
        # Get database
        db = client[MONGODB_DB_NAME]
        
        # Test basic operations
        test_collection = db["test_collection"]
        
        # Insert a document
        result = await test_collection.insert_one({"test": "value", "number": 42})
        print(f"✅ Inserted document with ID: {result.inserted_id}")
        
        # Find the document
        found = await test_collection.find_one({"_id": result.inserted_id})
        print(f"✅ Found document: {found}")
        
        # Clean up
        await test_collection.delete_many({})
        print("✅ Cleaned up test documents")
        
        # List all collections
        collections = await db.list_collection_names()
        print(f"📂 Collections in database: {', '.join(collections) if collections else 'None'}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        # Close the connection
        client.close()
        print("✅ Connection closed")

if __name__ == "__main__":
    asyncio.run(test_connection())
