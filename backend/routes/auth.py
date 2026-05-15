from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from models.schemas import UserCreate, UserProfile, TierInfo
from dotenv import load_dotenv
from jose import JWTError, jwt
import os
import logging
import traceback
from services.database import GraphService
from services.auth_logic import hash_password, verify_password, create_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
db = GraphService()

load_dotenv()

SECRET_KEY = os.getenv("AUTH_SECRET_KEY") or os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


def _ensure_db_available():
    if not db.is_available():
        raise HTTPException(status_code=503, detail="Database connection unavailable")


def _cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "*",
    }


# Simple in-memory fallback user store for environments where Neo4j is unavailable.
# This is a temporary development aid only and not for production use.
_in_memory_users = {}

def _get_user_by_email_fallback(email: str):
    return _in_memory_users.get(email)

def _create_user_fallback(user_dict: dict):
    _in_memory_users[user_dict['email']] = {
        'id': user_dict['id'],
        'name': user_dict.get('name'),
        'email': user_dict.get('email'),
        'password': user_dict.get('password'),
        'role': user_dict.get('role', 'Trader'),
        'trust_score': user_dict.get('trust_score', 43)
    }


@router.post("/register", response_model=UserProfile)
async def register_user(user: UserCreate):
    try:
        # Use real DB if available, otherwise fall back to in-memory store
        if db.is_available():
            # Check for existing email
            existing = db.get_user_by_email(user.email)
            if existing:
                return JSONResponse(status_code=400, content={"detail": "Email already registered"}, headers=_cors_headers())

            # Prepare and create user
            user_dict = user.model_dump()
            user_dict["password"] = hash_password(user.password)
            db.create_user_node(user_dict)
        else:
            # Fallback in-memory store
            if _get_user_by_email_fallback(user.email):
                return JSONResponse(status_code=400, content={"detail": "Email already registered"}, headers=_cors_headers())
            user_dict = user.model_dump()
            user_dict["password"] = hash_password(user.password)
            _create_user_fallback(user_dict)

        return UserProfile(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            location=user.location,
            trust_score=43,
            tier=TierInfo(name="New", color="#2196F3", next_milestone=45)
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("Registration error")
        tb = traceback.format_exc()
        logging.error(tb)
        return JSONResponse(status_code=503, content={"detail": f"Registration failed: {str(e)}"}, headers=_cors_headers())


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        # Use DB when available, else fallback to in-memory users
        if db.is_available():
            user = db.get_user_by_email(form_data.username)
            if not user or not verify_password(form_data.password, user['password']):
                return JSONResponse(status_code=401, content={"detail": "Invalid email or password"}, headers=_cors_headers())
            user_id = user['id']
        else:
            user = _get_user_by_email_fallback(form_data.username)
            if not user or not verify_password(form_data.password, user['password']):
                return JSONResponse(status_code=401, content={"detail": "Invalid email or password"}, headers=_cors_headers())
            user_id = user['id']

        access_token = create_access_token(data={"sub": user_id})
        return JSONResponse(status_code=200, content={"access_token": access_token, "token_type": "bearer"}, headers=_cors_headers())
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("Login error")
        tb = traceback.format_exc()
        logging.error(tb)
        return JSONResponse(status_code=503, content={"detail": f"Login failed: {str(e)}"}, headers=_cors_headers())


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        # Try DB first, fallback to in-memory store
        user = None
        if db.is_available():
            user = db.get_user_by_id(user_id)
        if not user:
            # Search fallback users by id
            for u in _in_memory_users.values():
                if u['id'] == user_id:
                    user = u
                    break
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/me", response_model=UserProfile)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserProfile(
        id=current_user["id"],
        name=current_user.get("name", "User"),
        email=current_user.get("email", ""),
        role=current_user.get("role", "Trader"),
        location={
            "city": current_user.get("city", "Unknown"),
            "state": current_user.get("state", "Unknown"),
            "country": current_user.get("country", "Nigeria"),
        },
        trust_score=current_user.get("trust_score", 43),
        tier=TierInfo(name="New", color="#2196F3", next_milestone=45),
    )