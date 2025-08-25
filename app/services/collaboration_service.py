from datetime import datetime
from typing import List, Dict, Optional, Tuple
from bson import ObjectId
from decimal import Decimal, ROUND_HALF_UP

from app.models.collaboration import Group, GroupExpense, ExpenseSplit, GroupMember
from app.models.user_model import User
from app.core.database import get_database

class CollaborationService:
    """Service for handling collaboration features"""
    
    @staticmethod
    async def calculate_balances(group_id: str) -> Dict[str, float]:
        """
        Calculate net balances for all group members
        Returns a dict with user_id as key and balance as value
        """
        db = get_database()
        
        # Get all expenses for the group
        expenses = await GroupExpense.find({"group_id": ObjectId(group_id)}).to_list()
        
        # Initialize balances
        balances = {}
        
        # Process each expense
        for expense in expenses:
            paid_by = str(expense.paid_by.id) if hasattr(expense.paid_by, 'id') else str(expense.paid_by)
            
            # Add to paid amount for the payer
            if paid_by not in balances:
                balances[paid_by] = 0
            balances[paid_by] += float(expense.amount)
            
            # Subtract owed amount for each split
            for split in expense.splits:
                user_id = str(split.user_id.id) if hasattr(split.user_id, 'id') else str(split.user_id)
                if user_id not in balances:
                    balances[user_id] = 0
                balances[user_id] -= float(split.amount)
        
        # Process settlements
        settlements = await db.settlements.find({"group_id": ObjectId(group_id)}).to_list()
        
        for settlement in settlements:
            from_user = str(settlement['from_user_id'])
            to_user = str(settlement['to_user_id'])
            amount = float(settlement['amount'])
            
            if from_user not in balances:
                balances[from_user] = 0
            if to_user not in balances:
                balances[to_user] = 0
                
            balances[from_user] -= amount
            balances[to_user] += amount
        
        return balances
    
    @staticmethod
    async def calculate_settlements(group_id: str) -> List[Dict]:
        """
        Calculate minimum number of transactions to settle all debts in the group
        Returns a list of settlement transactions
        """
        balances = await CollaborationService.calculate_balances(group_id)
        
        # Convert to list of (user_id, balance) and filter out zeros
        balances_list = [(user_id, Decimal(str(balance)).quantize(Decimal('0.01'), ROUND_HALF_UP))
                        for user_id, balance in balances.items()
                        if balance != 0]
        
        # Separate debtors and creditors
        debtors = [(user_id, -amount) for user_id, amount in balances_list if amount < 0]
        creditors = [(user_id, amount) for user_id, amount in balances_list if amount > 0]
        
        settlements = []
        
        # Greedy algorithm to settle debts
        i = j = 0
        while i < len(debtors) and j < len(creditors):
            debtor_id, debt = debtors[i]
            creditor_id, credit = creditors[j]
            
            # Calculate the amount that can be settled in this transaction
            amount = min(debt, credit)
            
            if amount > 0:
                settlements.append({
                    'from_user_id': debtor_id,
                    'to_user_id': creditor_id,
                    'amount': float(amount)
                })
            
            # Update remaining debts/credits
            if debt > credit:
                debtors[i] = (debtor_id, debt - credit)
                j += 1
            elif debt < credit:
                creditors[j] = (creditor_id, credit - debt)
                i += 1
            else:
                i += 1
                j += 1
        
        return settlements
    
    @staticmethod
    async def add_expense(
        group_id: str,
        paid_by: str,
        amount: float,
        currency: str,
        description: str,
        category: str,
        splits: List[Dict],
        date: datetime = None
    ) -> GroupExpense:
        """
        Add a new group expense and update member balances
        """
        if date is None:
            date = datetime.utcnow()
        
        # Create expense splits
        expense_splits = [
            ExpenseSplit(
                user_id=split['user_id'],
                amount=split['amount'],
                is_paid=False
            )
            for split in splits
        ]
        
        # Create the expense
        expense = GroupExpense(
            group_id=ObjectId(group_id),
            paid_by=ObjectId(paid_by),
            amount=amount,
            currency=currency,
            description=description,
            category=category,
            date=date,
            splits=expense_splits,
            is_settled=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        await expense.create()
        return expense
    
    @staticmethod
    async def get_group_summary(group_id: str) -> Dict:
        """
        Get a summary of group finances
        """
        group = await Group.get(group_id, fetch_links=True)
        if not group:
            raise ValueError("Group not found")
        
        # Get all expenses
        expenses = await GroupExpense.find({"group_id": ObjectId(group_id)}).to_list()
        
        # Calculate total spent
        total_spent = sum(expense.amount for expense in expenses)
        
        # Calculate per-category spending
        category_spending = {}
        for expense in expenses:
            if expense.category not in category_spending:
                category_spending[expense.category] = 0
            category_spending[expense.category] += expense.amount
        
        # Get member balances
        balances = await CollaborationService.calculate_balances(group_id)
        
        # Get recent activity
        recent_expenses = sorted(expenses, key=lambda x: x.date, reverse=True)[:5]
        
        return {
            "total_members": len(group.members),
            "total_expenses": len(expenses),
            "total_spent": total_spent,
            "category_spending": category_spending,
            "member_balances": balances,
            "recent_activity": recent_expenses
        }
