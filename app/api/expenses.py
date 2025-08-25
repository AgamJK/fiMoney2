from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional

router = APIRouter()

class ExpenseCategory(str, Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    SHOPPING = "shopping"    
    BILLS = "bills"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    TRAVEL = "travel"
    EDUCATION = "education"
    INVESTMENT = "investment"
    OTHER = "other"

class Transaction(BaseModel):
    id: str
    date: str
    amount: float
    currency: str = "INR"
    merchant: str
    category: ExpenseCategory
    is_recurring: bool = False
    is_subscription: bool = False

class ExpenseAnalysis(BaseModel):
    total_spent: float
    currency: str = "INR"
    period_start: str
    period_end: str
    category_breakdown: Dict[str, float]
    top_expenses: List[Transaction]
    monthly_average: Optional[float] = None
    change_percentage: Optional[float] = None
    potential_savings: Optional[float] = None
    detected_anomalies: Optional[List[Dict[str, Any]]] = None

@router.get("/analysis", response_model=ExpenseAnalysis)
async def analyze_expenses(
    months: int = Query(6, ge=1, le=24, description="Number of months to analyze"),
    detect_anomalies: bool = Query(True, description="Enable anomaly detection"),
    # token: str = Depends(oauth2_scheme)  # Uncomment when auth is implemented
):
    """
    Analyze user's expenses and identify spending patterns
    
    Args:
        months: Number of months of historical data to analyze (1-24)
        detect_anomalies: Whether to run anomaly detection on expenses
        
    Returns:
        Detailed expense analysis including category breakdown and potential savings
    """
    try:
        # TODO: Replace with actual MCP API call
        # This is mock data for demonstration
        now = datetime.utcnow()
        period_end = now.replace(day=1) - timedelta(days=1)  # End of last month
        period_start = (period_end.replace(day=1) - timedelta(days=(months-1)*30)).replace(day=1)
        
        # Mock transactions
        transactions = [
            {
                "id": f"txn_{i}",
                "date": (period_end - timedelta(days=i)).strftime("%Y-%m-%d"),
                "amount": 500 + (i % 5) * 100,
                "merchant": ["Swiggy", "Zomato", "BigBasket", "DMart", "Apollo Pharmacy"][i % 5],
                "category": [ExpenseCategory.FOOD, ExpenseCategory.SHOPPING, 
                            ExpenseCategory.HEALTH, ExpenseCategory.BILLS][i % 4],
                "is_recurring": i % 3 == 0,
                "is_subscription": i % 5 == 0
            } for i in range(30 * months)  # ~30 transactions per month
        ]
        
        # Calculate category breakdown
        category_totals = {}
        for txn in transactions:
            category = txn["category"]
            category_totals[category] = category_totals.get(category, 0) + txn["amount"]
        
        total_spent = sum(t["amount"] for t in transactions)
        
        # Get top 5 largest expenses
        top_expenses = sorted(transactions, key=lambda x: x["amount"], reverse=True)[:5]
        
        # Simple anomaly detection (mock)
        anomalies = []
        if detect_anomalies:
            # Look for unusually large transactions (2x average)
            avg_amount = total_spent / len(transactions)
            for txn in transactions:
                if txn["amount"] > avg_amount * 2:
                    anomalies.append({
                        "type": "unusually_large_transaction",
                        "transaction_id": txn["id"],
                        "amount": txn["amount"],
                        "date": txn["date"],
                        "merchant": txn["merchant"],
                        "severity": "high" if txn["amount"] > avg_amount * 3 else "medium"
                    })
            
            # Check for duplicate transactions
            seen = {}
            for txn in transactions:
                key = (txn["amount"], txn["merchant"], txn["date"])
                if key in seen:
                    anomalies.append({
                        "type": "possible_duplicate",
                        "transaction_id": txn["id"],
                        "duplicate_of": seen[key],
                        "amount": txn["amount"],
                        "date": txn["date"],
                        "merchant": txn["merchant"]
                    })
                else:
                    seen[key] = txn["id"]
        
        # Calculate potential savings (mock)
        potential_savings = sum(
            txn["amount"] * 0.2  # 20% of subscription costs as potential savings
            for txn in transactions 
            if txn["is_subscription"]
        )
        
        return {
            "total_spent": round(total_spent, 2),
            "currency": "INR",
            "period_start": period_start.strftime("%Y-%m-%d"),
            "period_end": period_end.strftime("%Y-%m-%d"),
            "category_breakdown": {k: round(v, 2) for k, v in category_totals.items()},
            "top_expenses": top_expenses,
            "monthly_average": round(total_spent / months, 2),
            "change_percentage": -5.5,  # Mock: 5.5% decrease from previous period
            "potential_savings": round(potential_savings, 2) if potential_savings > 0 else None,
            "detected_anomalies": anomalies if anomalies else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
