from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Dict, Any, List, Optional
from uuid import UUID

from app.models.user import User
from app.core.security import get_current_active_user
from app.services.mcp_sync_service import get_mcp_sync_service, MCPSyncService
from app.services.ai_insight_service import get_ai_insight_service, AIInsightService
from app.core.fi_mcp_client import get_fi_mcp_client, FiMCPClient
from app.db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/sync", response_model=Dict[str, Any])
async def sync_financial_data(
    current_user: User = Depends(get_current_active_user),
    sync_service: MCPSyncService = Depends(get_mcp_sync_service)
):
    """
    Sync financial data from Fi's MCP Server.
    """
    return await sync_service.sync_user_data(str(current_user.id))

@router.get("/net-worth", response_model=Dict[str, Any])
async def get_net_worth(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    mcp_client: FiMCPClient = Depends(get_fi_mcp_client)
):
    """
    Get net worth trend over time.
    """
    try:
        return await mcp_client.get_net_worth_trend(str(current_user.id), days=days)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/credit-score", response_model=Dict[str, Any])
async def get_credit_score(
    current_user: User = Depends(get_current_active_user),
    mcp_client: FiMCPClient = Depends(get_fi_mcp_client)
):
    """
    Get user's credit score information.
    """
    try:
        return await mcp_client.get_credit_score(str(current_user.id))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/epf", response_model=Dict[str, Any])
async def get_epf_details(
    current_user: User = Depends(get_current_active_user),
    mcp_client: FiMCPClient = Depends(get_fi_mcp_client)
):
    """
    Get user's EPF (Employee Provident Fund) details.
    """
    try:
        return await mcp_client.get_epf_details(str(current_user.id))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/assets", response_model=List[Dict[str, Any]])
async def get_assets(
    current_user: User = Depends(get_current_active_user),
    mcp_client: FiMCPClient = Depends(get_fi_mcp_client)
):
    """
    Get user's assets.
    """
    try:
        return await mcp_client.get_assets(str(current_user.id))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/liabilities", response_model=List[Dict[str, Any]])
async def get_liabilities(
    current_user: User = Depends(get_current_active_user),
    mcp_client: FiMCPClient = Depends(get_fi_mcp_client)
):
    """
    Get user's liabilities.
    """
    try:
        return await mcp_client.get_liabilities(str(current_user.id))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/ai-insights", response_model=Dict[str, Any])
async def get_ai_insights(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    insight_service: AIInsightService = Depends(get_ai_insight_service)
):
    """
    Generate AI-powered financial insights.
    This may take some time to process.
    """
    try:
        # In a real implementation, you might want to run this in a background task
        # and notify the user when it's done, since it could take some time
        return await insight_service.generate_insights(str(current_user.id))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI insights: {str(e)}"
        )
