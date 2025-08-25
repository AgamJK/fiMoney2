from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from fastapi.encoders import jsonable_encoder
from pymongo import ReturnDocument
from bson import ObjectId

from app.core.security import get_current_active_user
from app.models.user_model import User
from app.models.collaboration import Group, GroupMember, MemberRole, GroupExpense, ExpenseSplit
from app.schemas.collaboration import (
    GroupCreate, GroupResponse, GroupUpdate, MemberResponse, MemberUpdate,
    GroupExpenseCreate, GroupExpenseResponse, GroupExpenseUpdate,
    SettlementCreate, SettlementResponse, GroupListResponse
)
from app.crud.base import get_document
from app.db.session import get_database

router = APIRouter()

# Helper functions
async def get_group_or_404(group_id: str, current_user: User) -> Group:
    group = await Group.get(group_id, fetch_links=True)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if user is a member of the group
    if not any(str(member.user_id.id) == str(current_user.id) for member in group.members):
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    return group

# Group endpoints
@router.post("/groups/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_in: GroupCreate,
    current_user: User = Depends(get_current_active_user),
):
    """Create a new collaboration group"""
    # Create the group
    group = Group(
        **group_in.dict(exclude={"initial_members"}),
        created_by=current_user.id,
        members=[
            GroupMember(
                user_id=current_user.id,
                role=MemberRole.OWNER,
                permissions={
                    "can_edit_budget": True,
                    "can_invite": True,
                    "can_remove_members": True
                }
            )
        ]
    )
    
    # Add initial members if any
    if group_in.initial_members:
        # TODO: Look up users by email and add them as members
        pass
    
    await group.create()
    
    # Add group to user's memberships
    current_user.group_memberships.append(group)
    await current_user.save()
    
    return group

@router.get("/groups/", response_model=GroupListResponse)
async def list_groups(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
):
    """List all groups the current user is a member of"""
    query = Group.find({"members.user_id": current_user.id})
    total = await query.count()
    groups = await query.skip(skip).limit(limit).to_list()
    
    return {
        "items": groups,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }

@router.get("/groups/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Get details of a specific group"""
    group = await get_group_or_404(group_id, current_user)
    return group

@router.put("/groups/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: str,
    group_in: GroupUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """Update group details"""
    group = await get_group_or_404(group_id, current_user)
    
    # Check if user has permission to update the group
    member = next((m for m in group.members if str(m.user_id.id) == str(current_user.id)), None)
    if not member or member.role not in [MemberRole.OWNER, MemberRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized to update this group")
    
    update_data = group_in.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    updated_group = await Group.find_one(Group.id == group_id).update({"$set": update_data})
    if not updated_group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    return await Group.get(group_id)

# Member endpoints
@router.get("/groups/{group_id}/members", response_model=List[MemberResponse])
async def list_group_members(
    group_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """List all members of a group"""
    group = await get_group_or_404(group_id, current_user)
    
    # Enhance member data with user details
    members_with_details = []
    for member in group.members:
        user = await User.get(member.user_id.id)
        member_dict = member.dict()
        member_dict["user_email"] = user.email
        member_dict["user_name"] = user.full_name
        members_with_details.append(member_dict)
    
    return members_with_details

@router.post("/groups/{group_id}/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def add_group_member(
    group_id: str,
    member_in: MemberCreate,
    current_user: User = Depends(get_current_active_user),
):
    """Add a member to a group"""
    group = await get_group_or_404(group_id, current_user)
    
    # Check if user has permission to add members
    current_member = next((m for m in group.members if str(m.user_id.id) == str(current_user.id)), None)
    if not current_member or not current_member.permissions.get("can_invite", False):
        raise HTTPException(status_code=403, detail="Not authorized to add members")
    
    # Find user by email if user_id not provided
    if not member_in.user_id and not member_in.email:
        raise HTTPException(status_code=400, detail="Either user_id or email is required")
    
    if member_in.user_id:
        user = await User.get(member_in.user_id)
    else:
        user = await User.find_one({"email": member_in.email.lower()})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is already a member
    if any(str(m.user_id.id) == str(user.id) for m in group.members):
        raise HTTPException(status_code=400, detail="User is already a member of this group")
    
    # Add user to group
    new_member = GroupMember(
        user_id=user.id,
        role=member_in.role,
        permissions={
            "can_edit_budget": member_in.role in [MemberRole.OWNER, MemberRole.ADMIN],
            "can_invite": member_in.role in [MemberRole.OWNER, MemberRole.ADMIN],
            "can_remove_members": member_in.role == MemberRole.OWNER
        }
    )
    
    group.members.append(new_member)
    await group.save()
    
    # Add group to user's memberships
    user.group_memberships.append(group)
    await user.save()
    
    return {
        **new_member.dict(),
        "user_email": user.email,
        "user_name": user.full_name
    }

# Expense endpoints
@router.post("/groups/{group_id}/expenses", response_model=GroupExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_group_expense(
    group_id: str,
    expense_in: GroupExpenseCreate,
    current_user: User = Depends(get_current_active_user),
):
    """Create a new group expense"""
    group = await get_group_or_404(group_id, current_user)
    
    # Create the expense
    expense = GroupExpense(
        **expense_in.dict(exclude={"split_type"}),
        group_id=group.id,
        paid_by=current_user.id,
        is_settled=False
    )
    
    # Save the expense
    await expense.create()
    
    # TODO: Update group members' balances
    
    return expense

@router.get("/groups/{group_id}/expenses", response_model=List[GroupExpenseResponse])
async def list_group_expenses(
    group_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
):
    """List expenses for a group"""
    group = await get_group_or_404(group_id, current_user)
    
    expenses = await GroupExpense.find(
        {"group_id": group.id},
        skip=skip,
        limit=limit
    ).sort(-GroupExpense.date).to_list()
    
    # Enhance with user details
    enhanced_expenses = []
    for expense in expenses:
        expense_dict = expense.dict()
        paid_by_user = await User.get(expense.paid_by)
        expense_dict["paid_by_name"] = paid_by_user.full_name if paid_by_user else "Unknown"
        
        # Enhance splits with user details
        enhanced_splits = []
        for split in expense.splits:
            split_user = await User.get(split.user_id)
            enhanced_splits.append({
                **split.dict(),
                "user_name": split_user.full_name if split_user else "Unknown",
                "user_email": split_user.email if split_user else ""
            })
        expense_dict["splits"] = enhanced_splits
        
        enhanced_expenses.append(expense_dict)
    
    return enhanced_expenses

# Settlement endpoints
@router.post("/groups/{group_id}/settlements", response_model=SettlementResponse, status_code=status.HTTP_201_CREATED)
async def create_settlement(
    group_id: str,
    settlement_in: SettlementCreate,
    current_user: User = Depends(get_current_active_user),
):
    """Record a settlement between users"""
    group = await get_group_or_404(group_id, current_user)
    
    # Verify both users are group members
    from_user = await User.get(settlement_in.from_user_id)
    to_user = await User.get(settlement_in.to_user_id)
    
    if not from_user or not to_user:
        raise HTTPException(status_code=404, detail="One or both users not found")
    
    if not any(str(m.user_id.id) == str(from_user.id) for m in group.members) or \
       not any(str(m.user_id.id) == str(to_user.id) for m in group.members):
        raise HTTPException(status_code=400, detail="Both users must be group members")
    
    # Create settlement record
    db = get_database()
    settlement = await db.settlements.insert_one({
        **settlement_in.dict(),
        "group_id": group.id,
        "created_by": current_user.id,
        "created_at": datetime.utcnow()
    })
    
    # TODO: Update user balances
    
    return {
        "_id": str(settlement.inserted_id),
        **settlement_in.dict(),
        "group_id": group.id,
        "created_by": str(current_user.id),
        "created_at": datetime.utcnow(),
        "from_user_name": from_user.full_name,
        "to_user_name": to_user.full_name
    }
