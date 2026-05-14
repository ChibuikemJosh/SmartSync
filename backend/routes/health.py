from fastapi import APIRouter
from services.database import GraphService # Assuming your db class is here
import time

router = APIRouter()
db = GraphService()

@router.get("/")
async def health_check():
    """Checks if the API and Database are responsive"""
    start_time = time.time()
    
    db_status = "Healthy"
    try:
        # Run a tiny query to see if Neo4j is up
        with db.driver.session() as session:
            session.run("RETURN 1")
    except Exception as e:
        db_status = f"Unhealthy: {str(e)}"
    
    latency = round((time.time() - start_time) * 1000, 2)
    
    return {
        "status": "active",
        "timestamp": time.time(),
        "latency_ms": latency,
        "database": db_status,
        "environment": "Development/Hackathon"
    }

@router.get("/version")
async def get_version():
    return {"version": "2.0.0", "codename": "Eagle Eye"}