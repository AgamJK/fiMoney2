import httpx
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, status
from app import settings
import logging

logger = logging.getLogger(__name__)

class FiMCPClient:
    """Client for interacting with Fi's MCP Server."""
    
    def __init__(self):
        self.base_url = settings.MCP_API_URL.rstrip("/")
        self.api_key = settings.MCP_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an authenticated request to the MCP API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"MCP API error: {e}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"MCP API error: {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to connect to MCP service: {str(e)}"
            )
    
    async def get_financial_snapshot(self, user_id: str) -> Dict[str, Any]:
        """Get a complete financial snapshot for a user."""
        return await self._make_request("GET", f"/users/{user_id}/financial-snapshot")
    
    async def get_assets(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all assets for a user."""
        data = await self._make_request("GET", f"/users/{user_id}/assets")
        return data.get("assets", [])
    
    async def get_liabilities(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all liabilities for a user."""
        data = await self._make_request("GET", f"/users/{user_id}/liabilities")
        return data.get("liabilities", [])
    
    async def get_credit_score(self, user_id: str) -> Dict[str, Any]:
        """Get credit score information for a user."""
        return await self._make_request("GET", f"/users/{user_id}/credit-score")
    
    async def get_epf_details(self, user_id: str) -> Dict[str, Any]:
        """Get EPF (Employee Provident Fund) details for a user."""
        return await self._make_request("GET", f"/users/{user_id}/epf")
    
    async def get_net_worth_trend(self, user_id: str, days: int = 90) -> Dict[str, Any]:
        """Get net worth trend over time."""
        return await self._make_request("GET", f"/users/{user_id}/net-worth/trend?days={days}")

# Dependency to get the MCP client
def get_fi_mcp_client() -> FiMCPClient:
    return FiMCPClient()
