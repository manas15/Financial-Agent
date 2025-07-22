from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.api.routes import auth_routes, watchlist_routes, ai_agent_routes
from src.models.database import create_tables
from src.utils.config import config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Stock Research Tool API",
    description="AI-powered stock research and analysis using Claude AI and Yahoo Finance MCP integration",
    version="2.0.0",
    docs_url="/docs" if config.DEBUG else None,
    redoc_url="/redoc" if config.DEBUG else None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if config.DEBUG else ["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - AI Stock Research Tool (Simplified)
app.include_router(ai_agent_routes.router)      # Core AI functionality + MCP data
app.include_router(watchlist_routes.router)     # Research stock lists  
app.include_router(auth_routes.router)          # Basic authentication

@app.on_event("startup")
async def startup_event():
    """Initialize database and perform startup tasks"""
    try:
        # Create database tables
        create_tables()
        logger.info("Database tables created successfully")
        
        # Check for required API keys
        missing_keys = config.validate_required_keys()
        if missing_keys:
            logger.warning(f"Missing API keys: {missing_keys}")
        else:
            logger.info("All required API keys are configured")
            
    except Exception as e:
        logger.error(f"Startup error: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Financial Agent API",
        "version": "1.0.0",
        "status": "operational",
        "docs_url": "/docs" if config.DEBUG else "disabled"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # You could add database connectivity check here
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": "1.0.0"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}")
    
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail}
        )
    
    # For production, don't expose internal errors
    if not config.DEBUG:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )
    
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level="info"
    )