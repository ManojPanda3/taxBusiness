from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pymongo import MongoClient
from datetime import datetime, timedelta
from typing import Optional
from app.api.deps import DB
from app.core.settings import settings
import os

# JWT Configuration
jwt_secret = settings.jwt_secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()

# Utility Functions


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(users_collection, username: str):
    return await users_collection.find_one({"username": username})


def create_user(users_collection, username: str, password: str):
    user = {
        "username": username,
        "hashed_password": get_password_hash(password),
    }
    users_collection.insert_one(user)
    return user


async def authenticate_user(users_collection, username: str, password: str):
    user = await get_user(users_collection, username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    print(jwt_secret)
    encoded_jwt = jwt.encode(to_encode, jwt_secret, algorithm=ALGORITHM)
    return encoded_jwt

# Routes


@router.post("/register", response_model=dict)
async def register_user(db: DB, form_data: OAuth2PasswordRequestForm = Depends()):
    users_collection = db.users
    user = await get_user(users_collection, form_data.username)
    print("User...", user)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    create_user(users_collection, form_data.username, form_data.password)
    return {"msg": "User created successfully"}


@router.post("/token", response_model=dict)
async def login_for_access_token(db: DB, form_data: OAuth2PasswordRequestForm = Depends()):
    users_collection = db.users
    user = await authenticate_user(
        users_collection, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
