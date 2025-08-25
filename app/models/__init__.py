# Import all models here to make them available when importing from app.models
from .user import User, UserSettings
from .account import Account, AccountConnection
from .transaction import Transaction, RecurringTransaction, TransactionType, TransactionCategory
from .investment import Investment, InvestmentTransaction, InvestmentType, InvestmentStatus, InvestmentTransactionType
from .goal import FinancialGoal, GoalType, GoalStatus

# This allows for cleaner imports like: from app.models import User, Account, etc.
__all__ = [
    'User', 'UserSettings',
    'Account', 'AccountConnection',
    'Transaction', 'RecurringTransaction', 'TransactionType', 'TransactionCategory',
    'Investment', 'InvestmentTransaction', 'InvestmentType', 'InvestmentStatus', 'InvestmentTransactionType',
    'FinancialGoal', 'GoalType', 'GoalStatus'
]
