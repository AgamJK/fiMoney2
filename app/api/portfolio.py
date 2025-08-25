from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum

router = APIRouter()

class AssetType(str, Enum):
    MUTUAL_FUND = "mutual_fund"
    EQUITY = "equity"
    FIXED_INCOME = "fixed_income"
    CASH = "cash"
    OTHER = "other"

class Asset(BaseModel):
    id: str
    name: str
    type: AssetType
    current_value: float
    allocation_percentage: float
    return_1y: Optional[float] = None
    return_ytd: Optional[float] = None
    benchmark: Optional[str] = None
    benchmark_return: Optional[float] = None
    
class PortfolioResponse(BaseModel):
    total_value: float
    currency: str = "INR"
    assets: List[Asset]
    last_rebalanced: Optional[datetime] = None
    target_allocation: Optional[dict] = None
    
@router.get("/analysis", response_model=PortfolioResponse)
async def analyze_portfolio(
    benchmark: Optional[str] = Query("NIFTY50", description="Benchmark index for comparison"),
    # token: str = Depends(oauth2_scheme)  # Uncomment when auth is implemented
):
    """
    Analyze the user's investment portfolio
    
    Args:
        benchmark: Benchmark index to compare against (e.g., NIFTY50, SENSEX)
        
    Returns:
        Portfolio analysis including asset allocation and performance metrics
    """
    try:
        # TODO: Replace with actual MCP API call
        # This is mock data for demonstration
        assets = [
            {
                "id": "mf_axis_bluechip",
                "name": "Axis Bluechip Fund - Growth",
                "type": AssetType.MUTUAL_FUND,
                "current_value": 450000,
                "allocation_percentage": 0.45,
                "return_1y": 12.5,
                "return_ytd": 8.2,
                "benchmark": "NIFTY50",
                "benchmark_return": 10.1
            },
            {
                "id": "equity_tcs",
                "name": "TCS Ltd",
                "type": AssetType.EQUITY,
                "current_value": 350000,
                "allocation_percentage": 0.35,
                "return_1y": 15.2,
                "return_ytd": 12.8,
                "benchmark": "NIFTYIT",
                "benchmark_return": 14.5
            },
            {
                "id": "fd_icici",
                "name": "ICICI Bank FD",
                "type": AssetType.FIXED_INCOME,
                "current_value": 200000,
                "allocation_percentage": 0.20,
                "return_1y": 6.5,
                "return_ytd": 3.2
            }
        ]
        
        total_value = sum(asset["current_value"] for asset in assets)
        
        # Update allocation percentages based on current values
        for asset in assets:
            asset["allocation_percentage"] = round(asset["current_value"] / total_value, 2)
        
        return {
            "total_value": total_value,
            "currency": "INR",
            "assets": assets,
            "last_rebalanced": (datetime.utcnow() - timedelta(days=45)).isoformat(),
            "target_allocation": {
                "equity": 0.6,
                "fixed_income": 0.3,
                "cash": 0.1
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
