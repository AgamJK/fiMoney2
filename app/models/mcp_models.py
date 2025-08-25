from sqlalchemy import Column, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import uuid

class FinancialSnapshot(Base):
    """Stores a point-in-time snapshot of a user's financial position."""
    __tablename__ = "financial_snapshots"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    total_assets = Column(Float, nullable=False)
    total_liabilities = Column(Float, nullable=False)
    net_worth = Column(Float, nullable=False)
    raw_data = Column(JSON, nullable=True)  # Store complete raw response for reference

class Asset(Base):
    """Stores different types of assets for a user."""
    __tablename__ = "assets"
    
    id = Column(String, primary_key=True)  # ID from MCP
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # e.g., 'savings', 'investment', 'property'
    current_value = Column(Float, nullable=False)
    currency = Column(String(3), default="INR")
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    asset_metadata = Column('metadata', JSON, nullable=True)  # Additional asset-specific data

class Liability(Base):
    """Stores different types of liabilities for a user."""
    __tablename__ = "liabilities"
    
    id = Column(String, primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # e.g., 'credit_card', 'loan', 'mortgage'
    outstanding_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="INR")
    interest_rate = Column(Float, nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    liability_metadata = Column('metadata', JSON, nullable=True)  # Additional liability-specific data

class CreditScore(Base):
    """Stores credit score information for a user."""
    __tablename__ = "credit_scores"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Float, nullable=False)
    provider = Column(String, nullable=False)  # e.g., 'CIBIL', 'Experian'
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    factors = Column(JSON, nullable=True)  # Factors affecting the score

class EPFAccount(Base):
    """Stores EPF (Employee Provident Fund) account details."""
    __tablename__ = "epf_accounts"
    
    id = Column(String, primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    current_balance = Column(Float, nullable=False)
    employer_contribution = Column(Float, nullable=True)
    employee_contribution = Column(Float, nullable=True)
    interest_rate = Column(Float, nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    epf_metadata = Column('metadata', JSON, nullable=True)  # Additional EPF-specific data
