# backend/app/services/forecast_service.py
from datetime import datetime, timedelta
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


class ForecastService:
    async def predict_tax_liability(self, historical_data: List[Dict]) -> Dict:
        """Predict future tax liability based on historical data."""
        df = pd.DataFrame(historical_data)
        
        # Prepare data for prediction
        X = np.array(range(len(df))).reshape(-1, 1)
        y = df['amount'].values
        
        # Fit model
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict next 3 months
        future_months = np.array(range(len(df), len(df) + 3)).reshape(-1, 1)
        predictions = model.predict(future_months)
        
        return {
            "predictions": [
                {
                    "month": (datetime.now() + timedelta(days=30 * i)).strftime("%Y-%m"),
                    "predicted_amount": round(float(pred), 2)
                }
                for i, pred in enumerate(predictions, 1)
            ]
        }

    async def get_cash_flow_insights(self, expenses: List[Dict]) -> Dict:
        """Analyze expenses and provide cash flow optimization strategies."""
        df = pd.DataFrame(expenses)
        
        total_expenses = df['amount'].sum()
        avg_monthly = df.groupby(pd.Grouper(key='date', freq='M'))['amount'].sum().mean()
        
        categories = df.groupby('category')['amount'].agg(['sum', 'mean'])
        top_expenses = categories.nlargest(3, 'sum')
        
        return {
            "total_expenses": total_expenses,
            "average_monthly": avg_monthly,
            "top_expense_categories": top_expenses.to_dict('index'),
            "recommendations": [
                "Consider reducing spending in top expense categories",
                "Set up automatic tax payments for estimated quarterly taxes",
                "Review recurring subscriptions and services"
            ]
        }