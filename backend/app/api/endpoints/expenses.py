# backend/app/api/endpoints/expenses.py
from typing import List

from app.api.deps import DB, CurrentUser
from app.models.expense import Expense, ExpenseCreate, ReceiptResponse
from app.services.ocr_service import OCRService
from fastapi import APIRouter, File, UploadFile

router = APIRouter()
ocr_service = OCRService()

@router.post("/upload-receipt/", response_model=ReceiptResponse)
async def upload_receipt(
    db: DB,
    current_user: CurrentUser,
    file: UploadFile = File(...)
):
    contents = await file.read()
    receipt_data = await ocr_service.extract_receipt_data(contents)
    
    expense = {
        "user_id": current_user.id,
        **receipt_data,
        "receipt_image": file.filename
    }
    result = await db.expenses.insert_one(expense)
    
    return ReceiptResponse(
        id=str(result.inserted_id),
        **receipt_data
    )

@router.get("/list/", response_model=List[Expense])
async def list_expenses(
    db: DB,
    current_user: CurrentUser
):
    cursor = db.expenses.find({"user_id": current_user.id})
    expenses = await cursor.to_list(length=100)
    return [Expense(**expense, id=str(expense["_id"])) for expense in expenses]