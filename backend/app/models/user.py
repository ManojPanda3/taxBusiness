# backend/app/models/user.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: str
    hashed_password: str
    created_at: datetime = datetime.utcnow()

    class Config:
        from_attributes = True

class User(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True