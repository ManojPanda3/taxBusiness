# backend/app/api/endpoints/forecasting.py
from typing import Annotated, List

from app.api.deps import DB, get_current_user
from app.models.forecasting import CashFlowInsight, TaxPredictionResponse
from app.models.user import User
from app.services.forecast_service import ForecastService
from fastapi import APIRouter, Depends

router = APIRouter()
forecast_service = ForecastService()

@router.get("/tax-liability-prediction/", response_model=TaxPredictionResponse)
async def predict_tax_liability(
    current_user: Annotated[User, Depends(get_current_user)],
    db: DB
):
    cursor = db.expenses.find({"user_id": current_user.id})
    historical_data = await cursor.to_list(length=None)
    
    predictions = await forecast_service.predict_tax_liability(historical_data)
    return TaxPredictionResponse(**predictions)

@router.get("/cash-flow-insights/", response_model=CashFlowInsight)
async def get_cash_flow_insights(
    current_user: Annotated[User, Depends(get_current_user)],
    db: DB
):
    cursor = db.expenses.find({"user_id": current_user.id})
    expenses = await cursor.to_list(length=None)
    
    insights = await forecast_service.get_cash_flow_insights(expenses)
    return CashFlowInsight(**insights)