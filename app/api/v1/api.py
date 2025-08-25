from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, insights
from app.core.config import get_settings

settings = get_settings()
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(insights.router, prefix="/insights", tags=["Insights"])
