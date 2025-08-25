from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId

class MemberRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"

class GroupMember(BaseModel):
    """Represents a member within a group"""
    user_id: PydanticObjectId = Field(..., description="Reference to the user")
    role: MemberRole = Field(default=MemberRole.MEMBER, description="Role of the member in the group")
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    permissions: Dict[str, bool] = Field(
        default_factory=lambda: {
            "can_edit_budget": True,
            "can_invite": False,
            "can_remove_members": False
        }
    )

class Group(Document):
    """Represents a collaboration group for shared budgets"""
    name: str = Field(..., max_length=100, description="Name of the group")
    description: Optional[str] = Field(None, max_length=500)
    created_by: PydanticObjectId = Field(..., description="User ID of the group creator")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    members: List[GroupMember] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "default_currency": "INR",
            "notify_on_changes": True
        }
    )
    
    class Settings:
        name = "collaboration_groups"
        indexes = [
            [("created_by", 1)],
            [("members.user_id", 1)],
            [("updated_at", -1)]
        ]

class SharedBudget(Document):
    """Represents a budget that can be shared among group members"""
    group_id: PydanticObjectId = Field(..., description="Reference to the group")
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    amount: float = Field(..., gt=0, description="Total budget amount")
    currency: str = Field(default="INR", max_length=3)
    period_start: datetime
    period_end: datetime
    categories: Dict[str, float] = Field(
        default_factory=dict,
        description="Category-wise budget allocation (category: amount)"
    )
    created_by: PydanticObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "shared_budgets"
        indexes = [
            [("group_id", 1)],
            [("created_by", 1)],
            [("period_start", 1), ("period_end", 1)]
        ]

class ExpenseSplit(BaseModel):
    """Represents how an expense is split among group members"""
    user_id: PydanticObjectId
    amount: float = Field(..., gt=0)
    is_paid: bool = False
    paid_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GroupExpense(Document):
    """Represents an expense that's split among group members"""
    group_id: PydanticObjectId
    paid_by: PydanticObjectId = Field(..., description="User ID who paid the expense")
    amount: float = Field(..., gt=0)
    currency: str = Field(default="INR", max_length=3)
    description: str
    category: str
    date: datetime = Field(default_factory=datetime.utcnow)
    splits: List[ExpenseSplit] = Field(..., min_items=1)
    is_settled: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "group_expenses"
        indexes = [
            [("group_id", 1)],
            [("paid_by", 1)],
            [("date", -1)],
            [("category", 1)]
        ]
