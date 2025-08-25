import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError

# Set up logging
logger = logging.getLogger(__name__)

from app.core.security import (
    authenticate_user,
    create_user_access_token,
    get_password_hash,
    get_current_active_user,
    validate_password_strength,
    oauth2_scheme
)
from app.core.config import get_settings
from app.models.user_model import User, UserCreate, UserResponse
from app.models.token_model import RefreshToken

settings = get_settings()

router = APIRouter()

@router.post("/register", response_model=Dict[str, str], status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    request: Request
) -> Any:
    """
    Register a new user
    """
    logger.info(f"Starting registration for email: {user_in.email}")
    
    try:
        # Check if user already exists
        logger.info("Checking if user already exists...")
        existing_user = await User.find_one(User.email == user_in.email)
        if existing_user:
            error_msg = f"Email {user_in.email} is already registered"
            logger.warning(error_msg)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Create user in database
        logger.info("Creating user in database...")
        
        try:
            # Create and save the user in a single operation
            user = await User.create_user(user_in)
            logger.info(f"User created successfully with ID: {user.id}")
            
            # Generate tokens
            logger.info("Generating access token...")
            try:
                tokens = await create_user_access_token(user, request)
                logger.info("Access token generated successfully")
                return tokens
            except Exception as token_error:
                logger.error(f"Error generating tokens: {str(token_error)}", exc_info=True)
                # Clean up the user if token generation fails
                await user.delete()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={"error": "Failed to generate access token"}
                )
            
        except ValidationError as ve:
            error_detail = f"Validation error: {str(ve)}"
            logger.error(error_detail, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"error": "Validation error", "details": str(ve)}
            )
        except Exception as e:
            error_detail = f"Error during user creation: {str(e)}"
            logger.error(error_detail, exc_info=True)
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "User creation failed", "details": str(e)}
            )
            
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions as-is
        logger.error(f"HTTP Exception in user registration: {str(http_exc.detail)}")
        raise
        
    except Exception as e:
        error_detail = f"Unexpected error during registration: {str(e)}"
        logger.error(error_detail, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )

@router.post("/login", response_model=Dict[str, str])
async def login_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        user = await authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Generate tokens
        tokens = await create_user_access_token(user, request)
        
        return tokens
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login. Please try again."
        )

@router.post("/refresh-token", response_model=Dict[str, str])
async def refresh_token(
    request: Request,
    refresh_token: str = Body(..., embed=True),
) -> Any:
    """
    Refresh access token using refresh token
    """
    try:
        # Find the refresh token in the database
        token_doc = await RefreshToken.find_one({
            "token": refresh_token,
            "is_revoked": False,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not token_doc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        # Get the user
        user = await User.get(token_doc.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Generate new tokens
        tokens = await create_user_access_token(user, request)
        
        # Revoke the old refresh token
        token_doc.is_revoked = True
        token_doc.revoked_at = datetime.utcnow()
        await token_doc.save()
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not refresh token"
        )

@router.post("/logout")
async def logout(
    refresh_token: str = Body(..., embed=True),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, str]:
    """
    Log out by revoking the refresh token
    """
    try:
        success = await RefreshToken.revoke_token(refresh_token)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token"
            )
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during logout"
        )

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user information
    """
    return current_user
