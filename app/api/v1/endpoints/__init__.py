from fastapi import APIRouter
from . import auth, users, insights, collaboration

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(insights.router, prefix="/insights", tags=["Insights"])
api_router.include_router(collaboration.router, prefix="/collaboration", tags=["Collaboration"])
