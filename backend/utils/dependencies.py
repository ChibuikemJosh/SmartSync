from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os
from services.database import GraphService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
db = GraphService()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token: No user ID")
        
        user = db.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
            
        return user # This returns the dict with name, role, id, etc.
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")