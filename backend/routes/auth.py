import os
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from dotenv import load_dotenv

from models.schemas import UserCreate, UserProfile, TierInfo
from services.database import GraphService
from services.auth_logic import hash_password, verify_password, create_access_token

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
db = GraphService()

SECRET_KEY = os.getenv("AUTH_SECRET_KEY") or os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY not found in environment variables")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Temporary In-Memory Fallback
_in_memory_users = {}

class UserStore:
    """Helper to abstract DB vs In-Memory logic"""
    @staticmethod
    def get_by_email(email: str) -> Optional[dict]:
        try:
            if db.is_available():
                return db.get_user_by_email(email)
        except Exception as e:
            logging.warning(f"Database lookup failed for {email}: {e}. Checking fallback store.")
        return _in_memory_users.get(email)

    @staticmethod
    def get_by_id(user_id: str) -> Optional[dict]:
        try:
            if db.is_available():
                return db.get_user_by_id(user_id)
        except Exception:
            pass
        return next((u for u in _in_memory_users.values() if u['id'] == user_id), None)

    @staticmethod
    def save(user_dict: dict):
        try:
            if db.is_available():
                db.create_user_node(user_dict)
                return
        except Exception as e:
            logging.error(f"DB Save failed: {e}")
        _in_memory_users[user_dict['email']] = user_dict

# --- Dependencies ---

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = UserStore.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --- Routes ---

@router.post("/register", response_model=UserProfile)
async def register_user(user: UserCreate):
    try:
        if UserStore.get_by_email(user.email):
            raise HTTPException(status_code=400, detail="Email already registered")

        user_dict = user.model_dump()
        user_dict["password"] = hash_password(user.password)
        user_dict["trust_score"] = 43 # Default score
        
        UserStore.save(user_dict)

        return UserProfile(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            location=user.location,
            tier=TierInfo(name="New", color="#2196F3", next_milestone=45)
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.exception(f"Register failed for {user.email}: {e}")
        raise HTTPException(status_code=500, detail="Could not create account right now. Please try again.")

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = UserStore.get_by_email(form_data.username)
        
        if not user or not verify_password(form_data.password, user['password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid email or password"
            )

        access_token = create_access_token(data={"sub": user['id']})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logging.exception(f"Login failed for {form_data.username}: {e}")
        raise HTTPException(status_code=500, detail="Could not login right now. Please try again.")

@router.get("/me", response_model=UserProfile)
async def get_me(current_user: dict = Depends(get_current_user)):
    # Standardizing location format from dictionary or flat DB fields
    location_data = current_user.get("location", {
        "city": current_user.get("city", "Unknown"),
        "state": current_user.get("state", "Unknown"),
        "country": current_user.get("country", "Nigeria")
    })

    return UserProfile(
        id=current_user["id"],
        name=current_user.get("name", "User"),
        email=current_user.get("email", ""),
        role=current_user.get("role", "Trader"),
        location=location_data,
        trust_score=current_user.get("trust_score", 43),
        tier=TierInfo(name="New", color="#2196F3", next_milestone=45),
    )