"""
Health Check Routes
Basic health and status endpoints
"""

from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint
            
    Returns:
    Health status
    """
    return {
        "status": "healthy",
        "service": "SmartSync Backend",
        "version": "1.0.0"
    }
                                                            
                                                            
    @router.get("/ready")
    async def readiness_check():
        """
        Readiness check endpoint
                                                                        
        Returns:
        Readiness status
        """
        # TODO: Add database and external service checks
        return {
            "ready": True,
            "services": {
                "database": "connected",
                "squad_api": "configured",
                "ai_services": "ready"
            }
        }