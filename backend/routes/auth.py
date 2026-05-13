from fastapi import APIRouter, HTTPException
from models.schemas import UserCreate, UserProfile, TierInfo
from services.database import GraphService

router = APIRouter()
db = GraphService()

@router.post("/register", response_model=UserProfile)
async def register_user(user: UserCreate):
    try:
        # 1. Prepare data for Neo4j
        user_dict = user.dict()
        
        # 2. Save to Graph
        db.create_user_node(user_dict)
        
        # 3. Return the profile with the starting 'New' tier
        return UserProfile(
            id=user.id,
            name=user.name,
            role=user.role,
            location=user.location,
            trust_score=43,
            tier=TierInfo(name="New", color="#2196F3", next_milestone=45)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")