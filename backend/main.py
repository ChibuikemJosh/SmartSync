"""
SmartSync Backend - FastAPI Main Application
A smart economic engine for the Squad Hackathon 3.0
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Import routes
from routes.squad import router as squad_router
#from routes.ai import router as ai_router
from routes.health import router as health_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SmartSync Backend",
    description="Voice-ERP and OCR engine for informal traders",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, tags=["health"])
app.include_router(squad_router, prefix="/api/squad", tags=["squad"])
#app.include_router(ai_router, prefix="/api/ai", tags=["ai"])


@app.get("/")
async def root():
    """Root endpoint - API status"""
    return {
        "status": "SmartSync Backend is Running 🚀",
        "version": "1.0.0",
        "description": "Intelligent Economy Engine"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
