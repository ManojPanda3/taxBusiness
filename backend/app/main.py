# backend/app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth, expenses, tax_alerts, forecasting
from app.api.deps import define_db_management

app = FastAPI(title="Tax Management System")
define_db_management(app)
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(expenses.router, prefix="/api/expenses", tags=["expenses"])
app.include_router(tax_alerts.router,
                   prefix="/api/tax-alerts", tags=["tax-alerts"])
app.include_router(forecasting.router,
                   prefix="/api/forecasting", tags=["forecasting"])
