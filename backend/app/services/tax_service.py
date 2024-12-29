# backend/app/services/tax_service.py
from datetime import datetime
from typing import Dict, List

import taxjar
from app.core.settings import settings


class TaxService:
    def __init__(self):
        self.client = taxjar.Client(api_key=settings.taxjar_api_key)

    async def get_tax_alerts(self) -> List[Dict]:
        """Get tax law changes and filing deadlines."""
        # This is a mock implementation - TaxJar doesn't actually provide this
        # You'd want to implement your own tax alert system or use a different API
        current_month = datetime.now().month
        alerts = []

        if current_month == 3:
            alerts.append({
                "type": "deadline",
                "message": "Q1 estimated tax payment due April 15",
                "due_date": "2024-04-15"
            })

        return alerts

    async def calculate_tax_liability(self, amount: float, state: str) -> Dict:
        """Calculate sales tax for a given amount and location."""
        try:
            tax = self.client.tax_for_order({
                'from_country': 'US',
                'from_state': state,
                'amount': amount,
                'shipping': 0
            })
            return {
                "amount": amount,
                "tax_amount": tax.amount_to_collect,
                "tax_rate": tax.rate
            }
        except taxjar.exceptions.TaxJarError as e:
            return {"error": str(e)}
