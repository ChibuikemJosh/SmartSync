from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from models.schemas import UserCreate, UserProfile, TierInfo
from dotenv import load_dotenv
from jose import JWTError, jwt
import os
from services.database import GraphService
from services.auth_logic import hash_password, verify_password, create_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
db = GraphService()

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

@router.post("/register", response_model=UserProfile)
async def register_user(user: UserCreate):
    
    if db.get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        # 1. Prepare data for Neo4j
        user_dict = user.model_dump()  # Convert Pydantic model to dict

        user_dict["password"] = hash_password(user.password)
        
        # 2. Save to Graph
        db.create_user_node(user_dict)
        
        # 3. Return the profile with the starting 'New' tier
        return UserProfile(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            location=user.location,
            trust_score=43,
            tier=TierInfo(name="New", color="#2196F3", next_milestone=45)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": user['id']})
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")