from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo import ReturnDocument

from app.core.security import get_current_active_user, get_current_active_superuser
from app.models.user_model import User, UserResponse, UserUpdate

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Retrieve users (admin only)
    """
    users = await User.find().skip(skip).limit(limit).to_list()
    return users

@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user
    """
    return current_user

@router.patch("/me", response_model=UserResponse)
async def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update own user
    """
    update_data = user_in.dict(exclude_unset=True)
    
    # Remove password if included (should be handled separately)
    if "password" in update_data:
        del update_data["password"]
    
    # Update user
    updated_user = await User.get(current_user.id).set(update_data)
    await updated_user.save()
    return updated_user

@router.get("/{user_id}", response_model=UserResponse)
async def read_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get a specific user by id (admin only)
    """
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update a user (admin only)
    """
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_data = user_in.dict(exclude_unset=True)
    
    # Remove password if included (should be handled separately)
    if "password" in update_data:
        del update_data["password"]
    
    # Update user
    updated_user = await user.set(update_data)
    await updated_user.save()
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_active_superuser),
) -> None:
    """
    Delete a user (admin only)
    """
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await user.delete()
    return None
