# backend/app/api/deps.py
from typing import Annotated, Any
from app.models.user import User
from fastapi import Depends, HTTPException, status
from app.core.settings import settings
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorClient

# OAuth2PasswordBearer instance
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")
client = None


def define_db_management(app):
    global client

    @app.on_event("startup")
    async def startup_db_client():
        global client
        client = AsyncIOMotorClient(settings.mongodb_uri)

    @app.on_event("shutdown")
    async def shutdown_db_client():
        global client
        client.close()


async def get_db():
    if not client:
        raise Exception("Error mongodb not started")
    db = client.taxBusiness
    yield db

# Dependency to get the current user


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncIOMotorClient = Depends(get_db)
) -> User:
    print("jwt %s" % settings.jwt_secret)
    try:
        # Decode the token
        payload = jwt.decode(token, settings.jwt_secret,
                             algorithms=["HS256"])
        user_name: str = payload.get("sub")
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
    user_data = await db.users.find_one({"username": user_name})
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Return the User object
    return User(
        id=str(user_data["_id"]),
        username=str(user_data["username"]),
        password=str(user_data["hashed_password"])
    )

# Annotated types for dependencies
DB = Annotated[Any, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
