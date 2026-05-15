import os
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from services.database import GraphService

# Initialize logging
logger = logging.getLogger(__name__)

# OAuth2 scheme points to your login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Database instance
db = GraphService()

# Configuration
SECRET_KEY = os.getenv("AUTH_SECRET_KEY") or os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency that validates the JWT token and returns the user object.
    Used to protect routes: @router.get("/me", dependencies=[Depends(get_current_user)])
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not SECRET_KEY:
        logger.critical("AUTH_SECRET_KEY is missing from environment variables!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication server configuration error"
        )

    try:
        # Decode the JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check 'sub' (standard) or 'id' (custom) fields
        user_id: str = payload.get("sub") or payload.get("id")
        
        if user_id is None:
            logger.warning("Token payload missing user identifier")
            raise credentials_exception

    except JWTError as e:
        logger.warning(f"JWT Decode error: {str(e)}")
        raise credentials_exception

    # Database Check
    if not db.is_available():
        logger.error("Database unavailable during user dependency check")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service temporarily unavailable"
        )

    # Fetch User Profile
    user = db.get_user_by_id(user_id)
    if user is None:
        logger.warning(f"User {user_id} not found in database but token was valid")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User no longer exists"
        )

    # Return the user dictionary (id, name, email, role, trust_score, etc.)
    return user