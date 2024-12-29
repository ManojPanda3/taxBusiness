# backend/app/models/expense.py
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ExpenseBase(BaseModel):
    amount: float
    date: datetime
    vendor: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    receipt_image: Optional[str] = None

class Expense(ExpenseBase):
    id: str
    user_id: str
    receipt_image: Optional[str] = None

    class Config:
        from_attributes = True

class ReceiptResponse(BaseModel):
    id: str
    amount: float
    date: Optional[datetime]
    vendor: Optional[str]
    receipt_image: Optional[str]