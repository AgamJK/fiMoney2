from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from app import settings

router = APIRouter()

class NetWorthDataPoint(BaseModel):
    date: str
    value: float
    currency: str = "INR"

class NetWorthResponse(BaseModel):
    current_value: float
    currency: str = "INR"
    trend: List[NetWorthDataPoint]
    change_percentage: Optional[float] = None
    last_updated: datetime

@router.get("/", response_model=NetWorthResponse)
async def get_net_worth(
    months: int = 12,
    # token: str = Depends(oauth2_scheme)  # Uncomment when auth is implemented
):
    """
    Get net worth data for the specified time period
    
    Args:
        months: Number of months of historical data to return (default: 12)
        
    Returns:
        NetWorthResponse with current value and historical data points
    """
    try:
        # TODO: Replace with actual MCP API call
        # This is mock data for demonstration
        now = datetime.utcnow()
        trend = []
        
        # Generate mock data points
        for i in range(months, -1, -1):
            date = (now - timedelta(days=30*i)).strftime("%Y-%m-%d")
            # Simulate growth with some random fluctuation
            base_value = 1000000 * (1 + (months - i) * 0.05)
            value = base_value * (0.95 + 0.1 * (i % 3))  # Add some variance
            trend.append({
                "date": date,
                "value": round(value, 2),
                "currency": "INR"
            })
        
        current_value = trend[-1]["value"] if trend else 0
        previous_value = trend[0]["value"] if len(trend) > 1 else current_value
        change_pct = ((current_value - previous_value) / previous_value * 100) if previous_value else 0
        
        return {
            "current_value": current_value,
            "currency": "INR",
            "trend": trend,
            "change_percentage": round(change_pct, 2),
            "last_updated": now.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
