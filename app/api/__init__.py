from fastapi import APIRouter

# Import v1 API router
from app.api.v1 import api_router as v1_router

# Import other endpoints using absolute paths
from app.api.endpoints import users, insights

api_router = APIRouter()

# Include v1 API endpoints
api_router.include_router(v1_router, prefix="/v1")

# Include other API endpoints
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(insights.router, prefix="/insights", tags=["Insights"])
