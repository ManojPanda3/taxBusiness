# backend/app/api/deps.py
from typing import Annotated, Any

from app.core.settings import settings
from app.models.user import User
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorClient

# OAuth2PasswordBearer instance
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

# Dependency to get the database connection


async def get_db():
    print(settings.mongodb_uri)
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client.taxBusiness
    try:
        yield db
    finally:
        client.close()

# Dependency to get the current user


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncIOMotorClient = Depends(get_db)
) -> User:

    try:
        # Decode the token
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        print(f"UserToken payload: {payload}")
        user_name: str = payload.get("sub")
        print(user_name)
        if not user_name:
            raise ValueError("User name not found in token")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    # geting user data from db
    user_data = await db.users.find_one({"username": "manoj_panda"})
    print(user_data)
    user_data = await db.users.find_one({"username": user_name})
    print(f"UserData : {user_data}")
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Return the User object
    return User(
        id=str(user_data["_id"]),
        username=user_data["username"],
        password=user_data["hashed_password"]
    )

# Annotated types for dependencies
DB = Annotated[Any, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

