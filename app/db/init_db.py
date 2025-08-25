import logging
from typing import Any, Optional
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import get_settings
from app.models.user_model import User, UserInDB
from app.core.security import get_password_hash

settings = get_settings()

logger = logging.getLogger(__name__)

async def init_db() -> None:
    """Initialize the database with the first superuser if it doesn't exist."""
    try:
        # Initialize Beanie with the User document
        from app.core.database import get_database
        db = await get_database().__anext__()
        
        # Check if superuser already exists
        superuser = await User.find_one(User.email == settings.FIRST_SUPERUSER_EMAIL)
        
        if not superuser:
            # Create superuser
            user_data = {
                "email": settings.FIRST_SUPERUSER_EMAIL,
                "hashed_password": get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                "full_name": "Initial Super User",
                "is_superuser": True,
                "is_verified": True,
                "is_active": True,
                "settings": {
                    "currency": "INR",
                    "timezone": "Asia/Kolkata",
                    "notification_preferences": {"email": True, "push": True, "sms": False},
                    "dashboard_preferences": {"default_view": "overview"}
                }
            }
            
            user = UserInDB(**user_data)
            await user.insert()
            logger.info(f"Created superuser: {settings.FIRST_SUPERUSER_EMAIL}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

async def get_database() -> Any:
    """Get the database instance."""
    from app.core.database import get_database as get_db
    return get_db()
    print("Database tables created successfully")
