# backend/app/api/endpoints/tax_alerts.py
from typing import List

from app.api.deps import get_current_user
from app.services.tax_service import TaxService
from fastapi import APIRouter, Depends

router = APIRouter()
tax_service = TaxService()

@router.get("/alerts/", response_model=List[dict])
async def get_tax_alerts(current_user: dict = Depends(get_current_user)):
    alerts = await tax_service.get_tax_alerts()
    return alerts

@router.post("/calculate-liability/", response_model=dict)
async def calculate_tax_liability(
    amount: float,
    state: str,
    current_user: dict = Depends(get_current_user)
):
    liability = await tax_service.calculate_tax_liability(amount, state)
    return liability