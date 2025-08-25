from datetime import datetime, timedelta
from typing import Optional, Any, Union, Dict, List, Tuple
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Request, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from bson import ObjectId
from app.core.config import get_settings
from app.core.password_utils import verify_password, get_password_hash
from app.models.token_model import RefreshToken
from app.models.user_model import User
import re
import secrets
import logging

settings = get_settings()

logger = logging.getLogger(__name__)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)

async def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate a user with email and password"""
    try:
        user = await User.find_one(User.email == email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    except Exception as e:
        logger.error(f"Error authenticating user {email}: {str(e)}")
        return None

def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Ensure user_id is a string
    if 'sub' in to_encode and isinstance(to_encode['sub'], ObjectId):
        to_encode['sub'] = str(to_encode['sub'])
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

async def create_refresh_token(user: User, request: Optional[Request] = None) -> str:
    """Create and store a refresh token"""
    refresh_token = await RefreshToken.create_token(
        user_id=user.id,  
        user_agent=request.headers.get("user-agent") if request else None,
        ip_address=request.client.host if request and hasattr(request, 'client') and request.client else None
    )
    return refresh_token.token

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a JWT token"""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.error(f"Token verification failed: {str(e)}")
        return None

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    authorization: Optional[str] = Header(None)
) -> User:
    """Get the current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Try to get token from Authorization header if not in the default location
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    
    if not token:
        raise credentials_exception
    
    try:
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
            
        # Ensure user_id is a string
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
            
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # Try to convert user_id to ObjectId if it's a string
        try:
            from bson import ObjectId
            if not isinstance(user_id, ObjectId):
                user_id = ObjectId(user_id)
        except Exception as e:
            logger.error(f"Invalid user_id format: {str(e)}")
            raise credentials_exception
            
        # Fetch user from database
        user = await User.get(user_id)
        if user is None:
            raise credentials_exception
            
        return user
        
    except JWTError as e:
        logger.error(f"JWT Error: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        )

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get the current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user

async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get the current active superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    return True, ""

async def create_user_access_token(user: User, request: Optional[Request] = None) -> Dict[str, str]:
    """Create access and refresh tokens for a user"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    refresh_token = await create_refresh_token(user, request)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": str(int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)),  # Convert to string
        "refresh_token": refresh_token
    }
