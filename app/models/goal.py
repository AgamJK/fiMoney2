from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, Integer, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum
import uuid
from datetime import datetime

class GoalStatus(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class GoalType(enum.Enum):
    RETIREMENT = "retirement"
    HOME_DOWNPAYMENT = "home_downpayment"
    VEHICLE = "vehicle"
    EDUCATION = "education"
    VACATION = "vacation"
    EMERGENCY_FUND = "emergency_fund"
    WEDDING = "wedding"
    START_BUSINESS = "start_business"
    OTHER = "other"

class FinancialGoal(Base):
    __tablename__ = "financial_goals"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Goal details
    name = Column(String(200), nullable=False)
    description = Column(String(1000))
    goal_type = Column(Enum(GoalType), nullable=False)
    status = Column(Enum(GoalStatus), default=GoalStatus.NOT_STARTED)
    
    # Target details
    target_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="INR")
    target_date = Column(DateTime(timezone=True), nullable=False)
    
    # Current progress
    current_amount = Column(Float, default=0.0)
    progress_percentage = Column(Float, default=0.0)
    
    # Investment strategy
    expected_return_rate = Column(Float, default=7.0)  # Annual return rate in percentage
    inflation_rate = Column(Float, default=6.0)  # Expected inflation rate
    
    # Recurring contributions
    monthly_contribution = Column(Float, default=0.0)
    contribution_frequency = Column(String(20), default="monthly")  # weekly, monthly, quarterly, yearly
    
    # Linked accounts
    linked_account_ids = Column(JSON, default=[])  # Account IDs contributing to this goal
    
    # Dates
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    completed_date = Column(DateTime(timezone=True))
    
    # Metadata
    is_primary = Column(Boolean, default=False)
    color_code = Column(String(7), default="#3B82F6")  # Default blue
    icon = Column(String(50))
    goal_metadata = Column('metadata', JSON, default={})
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="financial_goals")
    
    def __repr__(self):
        return f"<FinancialGoal(id={self.id}, name='{self.name}', target={self.target_amount} {self.currency})>"
    
    def calculate_progress(self):
        """Calculate and update progress percentage"""
        if self.target_amount > 0:
            self.progress_percentage = min(100.0, (self.current_amount / self.target_amount) * 100)
        else:
            self.progress_percentage = 0.0
        return self.progress_percentage
    
    def calculate_months_remaining(self):
        """Calculate months remaining until target date"""
        today = datetime.now().date()
        target = self.target_date.date()
        months = (target.year - today.year) * 12 + (target.month - today.month)
        return max(0, months)
    
    def calculate_required_monthly_savings(self):
        """Calculate required monthly savings to reach the goal"""
        months = self.calculate_months_remaining()
        if months == 0:
            return 0.0
            
        monthly_rate = (1 + self.expected_return_rate/100) ** (1/12) - 1
        future_value = self.target_amount - self.current_amount * ((1 + monthly_rate) ** months)
        
        if future_value <= 0:
            return 0.0
            
        return future_value * monthly_rate / (((1 + monthly_rate) ** months) - 1)
    
    def is_on_track(self):
        """Check if the goal is on track based on current progress"""
        if self.status == GoalStatus.COMPLETED:
            return True
            
        months_elapsed = (datetime.now().date() - self.start_date.date()).days / 30.44
        expected_progress = min(100, (months_elapsed / self.calculate_months_remaining()) * 100)
        return self.progress_percentage >= expected_progress * 0.9  # Allow 10% buffer
