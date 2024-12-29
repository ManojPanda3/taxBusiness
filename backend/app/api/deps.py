# backend/app/api/deps.py
from typing import Annotated, Any

from app.core.settings import settings
from app.models.user import User
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorClient

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

async def get_db():
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client.taxmanagement
    try:
        yield db
    finally:
        client.close()

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    db = AsyncIOMotorClient(settings.mongodb_uri).taxmanagement
    user_data = await db.users.find_one({"_id": user_id})
    if user_data is None:
        raise credentials_exception
    
    return User(
        id=str(user_data["_id"]),
        email=user_data["email"],
        full_name=user_data.get("full_name"),
        created_at=user_data["created_at"]
    )

DB = Annotated[Any, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]