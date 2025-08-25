from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import AsyncGenerator, Optional, List, Type, TYPE_CHECKING
import logging

from app.core.config import get_settings

# Import models in a way that avoids circular imports
if TYPE_CHECKING:
    from app.models.user_model import User
    from app.models.token_model import RefreshToken

settings = get_settings()
logger = logging.getLogger(__name__)

# MongoDB connection
client: Optional[AsyncIOMotorClient] = None

def get_mongo_client() -> AsyncIOMotorClient:
    """Get MongoDB client instance."""
    global client
    if client is None:
        client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=10,
            minPoolSize=3,
            tz_aware=True,
            connectTimeoutMS=settings.MONGODB_CONNECTION_TIMEOUT_MS,
            socketTimeoutMS=settings.MONGODB_SOCKET_TIMEOUT_MS,
            serverSelectionTimeoutMS=settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
            retryWrites=True,
            w='majority'
        )
    return client

async def init_beanie_db(connection_string: str = None, database_name: str = None):
    """Initialize Beanie with MongoDB connection."""
    global client
    
    # Use provided parameters or fall back to settings
    mongo_url = connection_string or settings.MONGODB_URL
    db_name = database_name or settings.MONGODB_DB_NAME
    
    if not mongo_url or not db_name:
        raise ValueError("MongoDB connection string and database name must be provided")
    
    # Get or create client
    client = get_mongo_client()
    
    try:
        # Test the connection
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB!")
        
        # Import models here to avoid circular imports
        from app.models.user_model import User
        from app.models.token_model import RefreshToken
        
        # Initialize Beanie with the models
        await init_beanie(
            database=client[db_name],
            document_models=[
                User,
                RefreshToken,
            ]
        )
        logger.info("Beanie initialized successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize Beanie: {e}")
        client = None
        raise

async def get_database() -> AsyncGenerator:
    """Get the MongoDB database instance."""
    global client
    
    if client is None:
        await init_beanie_db()
    
    try:
        yield client[settings.MONGODB_DB_NAME]
    except Exception as e:
        logger.error(f"Error getting database: {e}")
        raise

# For backward compatibility
get_db = get_database

async def close_db_connection():
    """Close the MongoDB connection."""
    global client
    if client is not None:
        try:
            client.close()
            logger.info("MongoDB connection closed.")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")
        finally:
            client = None
