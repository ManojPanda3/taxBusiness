# backend/app/models/forecasting.py
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class PredictionItem(BaseModel):
    month: str
    predicted_amount: float

class TaxPredictionResponse(BaseModel):
    predictions: List[PredictionItem]

class CashFlowInsight(BaseModel):
    total_expenses: float
    average_monthly: float
    top_expense_categories: dict
    recommendations: List[str]