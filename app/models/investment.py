from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, JSON, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum
import uuid

class InvestmentType(enum.Enum):
    MUTUAL_FUND = "mutual_fund"
    STOCK = "stock"
    FIXED_DEPOSIT = "fixed_deposit"
    PPF = "ppf"
    EPF = "epf"
    NPS = "nps"
    BOND = "bond"
    ETF = "etf"
    GOLD = "gold"
    REAL_ESTATE = "real_estate"
    CRYPTO = "crypto"
    OTHER = "other"

class InvestmentStatus(enum.Enum):
    ACTIVE = "active"
    SOLD = "sold"
    MATURED = "matured"
    CLOSED = "closed"

class Investment(Base):
    __tablename__ = "investments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(String(36), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    
    # Investment details
    name = Column(String(200), nullable=False)
    investment_type = Column(Enum(InvestmentType), nullable=False)
    status = Column(Enum(InvestmentStatus), default=InvestmentStatus.ACTIVE)
    
    # Identification
    symbol = Column(String(50))
    isin = Column(String(20))
    amfi_code = Column(String(20))
    
    # Investment amounts
    current_value = Column(Float, default=0.0)
    total_invested = Column(Float, default=0.0)
    units = Column(Float, default=0.0)
    nav = Column(Float)  # Net Asset Value per unit
    
    # Performance metrics
    xirr = Column(Float)  # Extended Internal Rate of Return
    absolute_return = Column(Float)
    annualized_return = Column(Float)
    
    # Dates
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    last_updated = Column(DateTime(timezone=True))
    
    # Metadata
    investment_metadata = Column('metadata', JSON, default={})  # For storing additional investment details
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    account = relationship("Account")
    transactions = relationship("InvestmentTransaction", back_populates="investment")
    
    def __repr__(self):
        return f"<Investment(id={self.id}, name={self.name}, type={self.investment_type.value})>"

class InvestmentTransactionType(enum.Enum):
    BUY = "buy"
    SELL = "sell"
    DIVIDEND = "dividend"
    INTEREST = "interest"
    SWITCH = "switch"
    SPLIT = "split"
    BONUS = "bonus"
    TAX = "tax"
    FEE = "fee"
    OTHER = "other"

class InvestmentTransaction(Base):
    __tablename__ = "investment_transactions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    investment_id = Column(String(36), ForeignKey("investments.id", ondelete="CASCADE"), nullable=False)
    
    # Transaction details
    transaction_type = Column(Enum(InvestmentTransactionType), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    settlement_date = Column(DateTime(timezone=True))
    
    # Amounts
    amount = Column(Float, nullable=False)
    units = Column(Float)
    price_per_unit = Column(Float)
    
    # Fees and taxes
    brokerage = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    other_charges = Column(Float, default=0.0)
    
    # References
    reference_id = Column(String(100))
    external_id = Column(String(100), index=True)
    
    # Metadata
    notes = Column(String(500))
    holding_metadata = Column('metadata', JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    investment = relationship("Investment", back_populates="transactions")
    
    def __repr__(self):
        return f"<InvestmentTransaction(id={self.id}, type={self.transaction_type.value}, amount={self.amount})>"
