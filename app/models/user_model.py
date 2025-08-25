from datetime import datetime
from typing import Optional, List, Any, Dict, TYPE_CHECKING, Union
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict, field_validator, model_validator
from pydantic.functional_validators import BeforeValidator
from pydantic_core import PydanticCustomError
from beanie import Document, Indexed, PydanticObjectId, Link
from bson import ObjectId
from passlib.context import CryptContext
import logging

# Import collaboration models
from app.models.collaboration import Group, GroupMember, MemberRole

# For type checking only
if TYPE_CHECKING:
    from app.schemas.user_schema import UserCreate, UserUpdate

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)

class PyObjectId(str):
    """Custom type for MongoDB ObjectId that works with Pydantic v2"""
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(
            cls.validate,
            serialization=core_schema.to_string_ser_schema(),
        )
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str):
            try:
                ObjectId(v)
                return v
            except Exception:
                pass
        raise ValueError("Invalid ObjectId")

class UserBase(BaseModel):
    """Base model for User data validation"""
    email: EmailStr = Field(..., description="User's email address")
    full_name: str = Field(..., min_length=2, max_length=255, description="User's full name")
    is_active: bool = Field(True, description="Whether the user is active")
    is_verified: bool = Field(False, description="Whether the user's email is verified")
    is_superuser: bool = Field(False, description="Whether the user is a superuser")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "is_active": True,
                "is_verified": False,
                "is_superuser": False
            }
        }
    )
    
    def update_modified(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()
        return self

class User(Document, UserBase):
    """User model for database operations"""
    id: Optional[PyObjectId] = Field(default_factory=lambda: PyObjectId(str(ObjectId())), alias="_id")
    hashed_password: str = Field(..., description="Hashed password")
    phone_number: Optional[str] = None
    settings: Optional[Dict[str, Any]] = {
        "currency": "INR",
        "timezone": "Asia/Kolkata",
        "notification_preferences": {"email": True, "push": True, "sms": False},
        "dashboard_preferences": {"default_view": "overview"},
        "collaboration": {
            "show_group_notifications": True,
            "default_split_type": "equal",
            "default_currency": "INR"
        }
    }
    
    # Group memberships
    group_memberships: List[Link[Group]] = Field(default_factory=list, description="Groups the user is a member of")
    
    class Settings:
        name = "users"
        indexes = [
            [("email", 1)],  # Index on email
            [("is_active", 1)],
            [("is_verified", 1)],
            [("is_superuser", 1)]
        ]
        use_state_management = True
    
    @field_validator('id', mode='before')
    @classmethod
    def validate_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str):
            try:
                ObjectId(v)
                return v
            except Exception:
                pass
        raise ValueError("Invalid ObjectId")
    
    def update_modified(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()
        return self
        
    @classmethod
    async def create_user(cls, user_create: 'UserCreate') -> 'User':
        """Create a new user from UserCreate model"""
        logger = logging.getLogger(__name__)
        try:
            logger.info(f"Creating user with email: {user_create.email}")
            
            # Check if user already exists
            existing_user = await cls.find_one({"email": user_create.email.lower()})
            if existing_user:
                raise ValueError("A user with this email already exists")
            
            # Create a new user instance with required fields
            user_data = {
                "email": user_create.email.lower(),
                "full_name": user_create.full_name,
                "hashed_password": get_password_hash(user_create.password),
                "is_active": True,
                "is_verified": False,
                "is_superuser": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            logger.info("User data prepared for creation")
            
            # Create and return the user instance
            try:
                # Create the user document directly in MongoDB
                user = cls(**user_data)
                await user.insert()
                logger.info(f"User created successfully with ID: {user.id}")
                return user
            except Exception as ve:
                logger.error(f"Error creating user in database: {str(ve)}", exc_info=True)
                if "duplicate key error" in str(ve).lower():
                    raise ValueError("A user with this email already exists")
                raise ValueError(f"Database error: {str(ve)}")
            
        except Exception as e:
            logger.error(f"Error in create_user: {str(e)}", exc_info=True)
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

class UserCreate(BaseModel):
    """User creation model"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="User's password. Must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number and one special character"
    )
    full_name: str = Field(..., min_length=2, max_length=255, description="User's full name")
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "TestPass123!",
                "full_name": "John Doe"
            }
        }
    )

class UserUpdate(User):
    """User update model"""
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_superuser: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "new.email@example.com",
                "full_name": "New Name",
                "phone_number": "+1234567890"
            }
        }
    }


class UserResponse(UserBase):
    """User response model (excludes sensitive data)"""
    id: str = Field(..., alias="_id")
    
    model_config = {
        "populate_by_name": True,
        "json_encoders": {"ObjectId": str},
        "json_schema_extra": {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "email": "user@example.com",
                "full_name": "John Doe",
                "is_active": True,
                "is_verified": False,
                "is_superuser": False,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        }
    }
