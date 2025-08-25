import logging
from datetime import datetime, timedelta
from typing import Optional, Any, Union
from beanie import Document, Indexed
from pydantic import Field
from bson import ObjectId
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class RefreshToken(Document):
    """Model for storing refresh tokens"""
    user_id: str = Field(indexed=True)
    token: str = Field(indexed=True)
    expires_at: datetime
    is_revoked: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    revoked_at: Optional[datetime] = None
    
    class Settings:
        name = "refresh_tokens"
        use_state_management = True
        ttl = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        @classmethod
        def get_collection_name(cls) -> str:
            return cls.name
            
    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True

    @classmethod
    async def create_token(
        cls, 
        user_id: Union[str, ObjectId],
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> 'RefreshToken':
        """Create a new refresh token"""
        try:
            # Convert user_id to string
            user_id_str = str(user_id)
            
            # First, revoke any existing tokens for this user
            await cls.find({"user_id": user_id_str, "is_revoked": False}).update_many({
                "$set": {"is_revoked": True, "revoked_at": datetime.utcnow()}
            })
            
            # Create new token
            token = cls(
                user_id=user_id_str,
                token=cls.generate_token(),
                expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
                user_agent=user_agent,
                ip_address=ip_address
            )
            await token.insert()
            return token
            
        except Exception as e:
            logger.error(f"Error creating refresh token: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def generate_token() -> str:
        """Generate a secure random token"""
        import secrets
        return secrets.token_urlsafe(64)

    @classmethod
    async def revoke_token(cls, token: str) -> bool:
        """Revoke a refresh token by token string"""
        token_doc = await cls.find_one({
            "token": token,
            "is_revoked": False,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if token_doc:
            token_doc.is_revoked = True
            token_doc.revoked_at = datetime.utcnow()
            await token_doc.save()
            return True
        return False
        
    @classmethod
    async def is_valid(cls, token: str) -> bool:
        """Check if a refresh token is valid"""
        token_doc = await cls.find_one({
            "token": token,
            "is_revoked": False,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        return token_doc is not None
