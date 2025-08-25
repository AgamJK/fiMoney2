import logging
import traceback
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from app.api.v1.endpoints import api_router
from app.core.config import get_settings
from app.core.database import init_beanie
from app.models.user_model import User

settings = get_settings()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Fi MCP + Gemini Finance Agent API",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

async def create_initial_data():
    """Create initial data in the database if needed."""
    try:
        from app.models.user_model import User
        # Check if we have any users
        user_count = await User.count()
        if user_count == 0:
            logger.info("No users found, creating initial admin user...")
            # Create initial admin user if needed
            pass
    except Exception as e:
        logger.error(f"Error creating initial data: {str(e)}", exc_info=True)

@app.on_event("startup")
async def startup_event():
    """Initialize services when the app starts."""
    try:
        logger.info("Starting application initialization...")
        
        # Initialize MongoDB connection and Beanie
        logger.info("Initializing database connection...")
        from app.core.database import init_beanie_db
        await init_beanie_db()
        logger.info("✅ MongoDB connection established and Beanie initialized")
        
        # Check if we need to create initial data
        await create_initial_data()
        
        # Initialize MCP client (non-blocking)
        try:
            from app.core.fi_mcp_client import FiMCPClient
            FiMCPClient()
            logger.info("✅ MCP client initialized")
        except Exception as e:
            logger.warning(f"⚠️  Could not initialize MCP client: {str(e)}")
        
        # Debug: Print all registered routes
        logger.info("\n=== Registered Routes ===")
        for route in app.routes:
            if hasattr(route, 'methods'):
                methods = ", ".join(route.methods) if hasattr(route, 'methods') else 'N/A'
                logger.info(f"{methods} {route.path}")
        logger.info("======================\n")
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Startup failed: {str(e)}"
        )

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up when the app shuts down."""
    from app.core.database import client
    
    if client:
        client.close()
        logger.info("✅ MongoDB connection closed")

@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Fi MCP + Gemini Finance Agent API",
        "docs": f"{settings.API_V1_STR}/docs",
        "version": settings.VERSION,
        "status": "operational"
    }

@app.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint"""
    from app.core.database import mongo_client
    
    try:
        # Check database connection
        await mongo_client.admin.command('ping')
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "disconnected"
    
    return {
        "status": "ok" if db_status == "connected" else "degraded",
        "database": db_status,
        "version": settings.VERSION
    }
