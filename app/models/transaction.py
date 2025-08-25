from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum
import uuid
from datetime import datetime

class TransactionType(enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    INVESTMENT = "investment"
    DIVIDEND = "dividend"
    INTEREST = "interest"
    FEE = "fee"
    REFUND = "refund"
    OTHER = "other"

class TransactionStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TransactionCategory(enum.Enum):
    # Income Categories
    SALARY = "salary"
    BUSINESS = "business"
    FREELANCE = "freelance"
    INVESTMENT_RETURN = "investment_return"
    RENTAL = "rental"
    GIFT = "gift"
    OTHER_INCOME = "other_income"
    
    # Expense Categories
    FOOD = "food"
    TRANSPORT = "transport"
    HOUSING = "housing"
    UTILITIES = "utilities"
    HEALTHCARE = "healthcare"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    TRAVEL = "travel"
    EDUCATION = "education"
    PERSONAL_CARE = "personal_care"
    DEBT = "debt"
    TAX = "tax"
    INSURANCE = "insurance"
    SUBSCRIPTION = "subscription"
    OTHER_EXPENSE = "other_expense"

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(String(36), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    
    # Transaction details
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="INR")
    transaction_type = Column(Enum(TransactionType), nullable=False)
    category = Column(Enum(TransactionCategory))
    subcategory = Column(String(50))
    description = Column(String(255))
    original_description = Column(String(255))
    
    # Dates
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    posted_date = Column(DateTime(timezone=True))
    
    # Status and metadata
    status = Column(Enum(TransactionStatus), default=TransactionStatus.COMPLETED)
    is_recurring = Column(Boolean, default=False)
    recurring_id = Column(String(100))
    is_duplicate = Column(Boolean, default=False)
    is_manually_added = Column(Boolean, default=False)
    
    # Merchant information
    merchant_name = Column(String(100))
    merchant_id = Column(String(100))
    
    # Location
    location = Column(JSON)
    
    # External references
    external_id = Column(String(100), index=True)
    external_account_id = Column(String(100))
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    
    # Indexes
    __table_args__ = (
        Index('idx_transaction_user_date', 'user_id', 'date'),
        Index('idx_transaction_account_date', 'account_id', 'date'),
        Index('idx_transaction_external', 'user_id', 'external_id', 'external_account_id', unique=True)
    )
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, type={self.transaction_type.value})>"

class RecurringTransaction(Base):
    __tablename__ = "recurring_transactions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(String(36), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    
    # Transaction template
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="INR")
    transaction_type = Column(Enum(TransactionType), nullable=False)
    category = Column(Enum(TransactionCategory))
    description = Column(String(255))
    
    # Recurrence pattern
    frequency = Column(String(20))  # daily, weekly, monthly, yearly
    interval = Column(Integer, default=1)  # Every N frequency units
    by_day = Column(String(20))  # For weekly/monthly patterns (e.g., "MO,TU,WE" or "1,15" for specific days)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    
    # Status
    is_active = Column(Boolean, default=True)
    last_occurrence = Column(DateTime(timezone=True))
    next_occurrence = Column(DateTime(timezone=True), index=True)
    
    # Metadata
    transaction_metadata = Column('metadata', JSON, default={})  # Using 'metadata' as the actual column name
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    account = relationship("Account")
    
    def __repr__(self):
        return f"<RecurringTransaction(id={self.id}, amount={self.amount}, frequency={self.frequency})>"
