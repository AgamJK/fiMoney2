from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, EmailStr, validator
from pydantic_core import PydanticCustomError
from bson import ObjectId

class MemberRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"

class MemberBase(BaseModel):
    """Base schema for group members"""
    user_id: str = Field(..., description="User ID of the member")
    role: MemberRole = Field(default=MemberRole.MEMBER, description="Role of the member in the group")
    
    class Config:
        json_encoders = {ObjectId: str}
        from_attributes = True

class MemberCreate(MemberBase):
    """Schema for adding a member to a group"""
    email: Optional[EmailStr] = Field(None, description="Email of the user to add (if not providing user_id)")

class MemberUpdate(BaseModel):
    """Schema for updating a member's role or permissions"""
    role: Optional[MemberRole] = None
    permissions: Optional[Dict[str, bool]] = None

class MemberResponse(MemberBase):
    """Response schema for group members"""
    joined_at: datetime
    permissions: Dict[str, bool]
    user_email: Optional[EmailStr] = None
    user_name: Optional[str] = None

class GroupBase(BaseModel):
    """Base schema for collaboration groups"""
    name: str = Field(..., max_length=100, description="Name of the group")
    description: Optional[str] = Field(None, max_length=500)

class GroupCreate(GroupBase):
    """Schema for creating a new group"""
    initial_members: Optional[List[str]] = Field(
        default_factory=list, 
        description="List of user emails to add as initial members"
    )

class GroupUpdate(GroupBase):
    """Schema for updating a group"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    settings: Optional[Dict[str, Any]] = None

class GroupResponse(GroupBase):
    """Response schema for group details"""
    id: str = Field(..., alias="_id")
    created_by: str
    created_at: datetime
    updated_at: datetime
    member_count: int
    settings: Dict[str, Any]
    
    class Config:
        json_encoders = {ObjectId: str}
        from_attributes = True
        populate_by_name = True

class GroupListResponse(BaseModel):
    """Response schema for listing groups"""
    items: List[GroupResponse]
    total: int
    page: int
    pages: int

class ExpenseSplitBase(BaseModel):
    """Base schema for expense splits"""
    user_id: str
    amount: float = Field(..., gt=0)
    is_paid: bool = False

class ExpenseSplitCreate(ExpenseSplitBase):
    """Schema for creating an expense split"""
    pass

class ExpenseSplitResponse(ExpenseSplitBase):
    """Response schema for expense splits"""
    paid_at: Optional[datetime] = None
    created_at: datetime
    user_email: Optional[str] = None
    user_name: Optional[str] = None

class GroupExpenseBase(BaseModel):
    """Base schema for group expenses"""
    amount: float = Field(..., gt=0)
    currency: str = Field(default="INR", max_length=3)
    description: str
    category: str
    date: datetime = Field(default_factory=datetime.utcnow)
    splits: List[ExpenseSplitCreate]

class GroupExpenseCreate(GroupExpenseBase):
    """Schema for creating a group expense"""
    split_type: str = Field("equal", description="How to split the expense: 'equal', 'amount', or 'percentage'")

class GroupExpenseUpdate(BaseModel):
    """Schema for updating a group expense"""
    description: Optional[str] = None
    category: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    date: Optional[datetime] = None
    is_settled: Optional[bool] = None

class GroupExpenseResponse(GroupExpenseBase):
    """Response schema for group expenses"""
    id: str = Field(..., alias="_id")
    group_id: str
    paid_by: str
    is_settled: bool
    created_at: datetime
    updated_at: datetime
    paid_by_name: Optional[str] = None
    splits: List[ExpenseSplitResponse]
    
    class Config:
        json_encoders = {ObjectId: str}
        from_attributes = True
        populate_by_name = True

class SettlementCreate(BaseModel):
    """Schema for creating a settlement between users"""
    from_user_id: str
    to_user_id: str
    amount: float = Field(..., gt=0)
    currency: str = Field(default="INR", max_length=3)
    description: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)

class SettlementResponse(SettlementCreate):
    """Response schema for settlements"""
    id: str = Field(..., alias="_id")
    group_id: str
    created_by: str
    created_at: datetime
    from_user_name: Optional[str] = None
    to_user_name: Optional[str] = None
    
    class Config:
        json_encoders = {ObjectId: str}
        from_attributes = True
        populate_by_name = True
