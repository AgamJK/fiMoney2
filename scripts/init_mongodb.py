#!/usr/bin/env python3
"""
Initialize MongoDB database with required collections and indexes.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from app.core.config import get_settings
from app.core.database import init_beanie_db, get_mongo_client
from app.models.user_model import User
from app.models.token_model import RefreshToken

settings = get_settings()

async def check_database_connection():
    """Check if we can connect to MongoDB."""
    try:
        client = get_mongo_client()
        await client.admin.command('ping')
        return True
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        return False

async def initialize_collections():
    """Initialize collections and create indexes."""
    try:
        # This will create collections and indexes defined in the models
        await init_beanie_db()
        
        # Verify collections exist
        client = get_mongo_client()
        db = client[settings.MONGODB_DB_NAME]
        collections = await db.list_collection_names()
        
        print("\n=== MongoDB Collections ===")
        for collection in collections:
            print(f"- {collection}")
            
            # Print indexes for each collection
            indexes = await db[collection].index_information()
            if indexes:
                print(f"  Indexes:")
                for name, index in indexes.items():
                    print(f"  - {name}: {index['key']}")
            
        return True
        
    except Exception as e:
        logging.error(f"Error initializing collections: {e}")
        return False

async def main():
    """Main function to initialize the database."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    print("\n=== Initializing MongoDB ===")
    
    # Check connection
    print("\n[1/3] Testing database connection...")
    if not await check_database_connection():
        print("❌ Failed to connect to MongoDB")
        return
    print("✅ Connected to MongoDB successfully")
    
    # Initialize collections and indexes
    print("\n[2/3] Initializing collections and indexes...")
    if not await initialize_collections():
        print("❌ Failed to initialize collections")
        return
    print("✅ Collections and indexes created successfully")
    
    print("\n=== MongoDB initialization complete! ===\n")

if __name__ == "__main__":
    asyncio.run(main())
