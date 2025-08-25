from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum
import uuid

class AccountType(enum.Enum):
    SAVINGS = "savings"
    CURRENT = "current"
    CREDIT_CARD = "credit_card"
    LOAN = "loan"
    INVESTMENT = "investment"
    WALLET = "wallet"
    OTHER = "other"

class AccountStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"
    FROZEN = "frozen"

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    account_number = Column(String(50), unique=True, index=True)
    institution = Column(String(100))
    balance = Column(Float, default=0.0)
    currency = Column(String(3), default="INR")
    status = Column(Enum(AccountStatus), default=AccountStatus.ACTIVE)
    is_primary = Column(Boolean, default=False)
    last_synced_at = Column(DateTime(timezone=True))
    account_metadata = Column('metadata', JSON, default={})  # For storing additional account details
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")
    
    def __repr__(self):
        return f"<Account(id={self.id}, name={self.name}, type={self.account_type.value})>"

class AccountConnection(Base):
    __tablename__ = "account_connections"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    institution_id = Column(String(100), nullable=False)
    institution_name = Column(String(100), nullable=False)
    access_token = Column(String(500))
    refresh_token = Column(String(500))
    status = Column(String(20), default="active")  # active, error, disconnected
    last_successful_sync = Column(DateTime(timezone=True))
    error_message = Column(String(500))
    connection_metadata = Column('metadata', JSON, default={})  # Using 'metadata' as the actual column name
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<AccountConnection(id={self.id}, institution={self.institution_name})>"
