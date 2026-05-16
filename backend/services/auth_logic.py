import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

# Initialize logging and environment
load_dotenv()
logger = logging.getLogger(__name__)

# ─── Configuration ──────────────────────────────────────────
# Oga, your SECRET_KEY is the padlock to your store. Keep it safe!
SECRET_KEY = os.getenv("AUTH_SECRET_KEY") or os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Default to 24 hours (1440 minutes) if not specified
try:
    token_expire_str = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(token_expire_str)
except ValueError:
    logger.warning("Invalid ACCESS_TOKEN_EXPIRE_MINUTES in env. Defaulting to 24h.")
    ACCESS_TOKEN_EXPIRE_MINUTES = 1440

# Password hashing setup
# PBKDF2 is more portable across hosting environments than bcrypt-only.
# Keep bcrypt in the verify list so any existing hashes still validate.
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")

# ─── Logic ──────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Turns a plain text password into a secure hash."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if the provided password matches the one in our records."""
    if not hashed_password:
        return False
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a JWT token for user authentication."""
    if not SECRET_KEY:
        logger.critical("AUTH_SECRET_KEY is missing! Authentication will fail.")
        raise RuntimeError("Environment variable AUTH_SECRET_KEY is not set.")

    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"JWT Encoding failed: {e}")
        raise RuntimeError("Could not generate access token.")