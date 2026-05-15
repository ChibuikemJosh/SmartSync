from fastapi import APIRouter, Response, status
from services.database import GraphService
import time
from datetime import datetime

router = APIRouter()
db = GraphService()

@router.get("/")
async def health_check(response: Response):
    """
    Checks if the API and Database are responsive.
    Returns 503 if the database is unreachable.
    """
    start_time = time.time()
    db_status = "Healthy"
    is_healthy = True

    try:
        # Check if driver exists and can execute a simple query
        with db._session() as session:
            # We use a simple RETURN 1 to verify connectivity
            session.run("RETURN 1").single()
    except Exception as e:
        db_status = f"Unhealthy: {str(e)}"
        is_healthy = False
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    latency_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "status": "active" if is_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "latency_ms": latency_ms,
        "database": db_status,
        "environment": "Development/Hackathon"
    }

@router.get("/version")
async def get_version():
    """Returns current API versioning info"""
    return {
        "version": "2.0.0", 
        "codename": "Eagle Eye",
        "last_updated": "2026-05-15"
    }