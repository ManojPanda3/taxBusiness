from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, status, File, UploadFile, Depends
from app.api.deps import DB, CurrentUser
from app.models.expense import Expense, ExpenseCreate, ReceiptResponse
from app.services.ocr_service import OCRService
from app.models.expense import ConfirmExpenseRequest
from bson import ObjectId

router = APIRouter()
ocr_service = OCRService()


@router.post("/upload-receipt/", response_model=ReceiptResponse)
async def upload_receipt(
    db: DB,
    current_user: CurrentUser,
    file: UploadFile = File(...)
):
    """
    Uploads a receipt, extracts data using OCR, and returns the analyzed data for user confirmation.
    """
    try:
        # Read file contents
        contents = await file.read()

        # Extract receipt data using OCR service
        receipt_data = await ocr_service.extract_receipt_data(contents)

        # Prepare data for user review
        analyzed_data = {
            "amount": receipt_data.get("total_amount", 0.0),
            "merchant": receipt_data.get("vendor", ""),
            # Add logic to extract or assign a category
            "category": receipt_data.get("category", "Uncategorized"),
            "upload_date": datetime.utcnow(),
            "is_tax_deductible": False,  # Default value until user confirms
            "deduction_reason": None,  # Default value until user provides input
            "receipt_image": file.filename,
            "date": receipt_data.get("date", ""),
            "invoice_number": receipt_data.get("invoice_number", ""),
            "tax_rate": receipt_data.get("tax_rate", 0.0),
            "tax_amount": receipt_data.get("tax_amount", 0.0),
            "items": receipt_data.get("items", [])
        }

        # Save the receipt data into the receipts collection
        result = await db.receipts.insert_one({
            "user_id": current_user.id,
            "amount": analyzed_data["amount"],
            "merchant": analyzed_data["merchant"],
            "category": analyzed_data["category"],
            "upload_date": analyzed_data["upload_date"],
            "is_tax_deductible": analyzed_data["is_tax_deductible"],
            "deduction_reason": analyzed_data["deduction_reason"],
            "receipt_image": analyzed_data["receipt_image"],
            "date": analyzed_data["date"],
            "invoice_number": analyzed_data["invoice_number"],
            "tax_rate": analyzed_data["tax_rate"],
            "tax_amount": analyzed_data["tax_amount"],
            "items": analyzed_data["items"]
        })

        return ReceiptResponse(
            **analyzed_data
        )
    except Exception as err:
        print(f"Error while processing receipt in upload_receipt: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process receipt"
        )


@router.post("/confirm-receipt/", response_model=Expense)
async def confirm_receipt(
    request: ConfirmExpenseRequest,
    db: DB,
    current_user: CurrentUser
):
    """
    Confirms the uploaded receipt data and saves it to the database.
    """
    try:
        # Prepare the expense data for insertion
        expense = {
            "user_id": current_user.id,
            "amount": request.amount,
            "merchant": request.merchant,
            "category": request.category,
            "receipt_image": request.receipt_image,
            "upload_date": request.upload_date,
            "is_tax_deductible": request.is_tax_deductible,
            "deduction_reason": request.deduction_reason
        }

        # Insert into MongoDB receipts collection
        result = await db.receipts.insert_one(expense)

        # Return the inserted document
        expense["_id"] = str(result.inserted_id)
        return Expense(**expense)
    except Exception as err:
        print(f"Error confirming receipt in confirm_receipt: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to confirm receipt"
        )


@router.get("/list/", response_model=List[Expense])
async def list_expenses(
    db: DB,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 10
):
    """
    Lists all expenses for the current user with optional pagination.
    """
    cursor = db.expenses.find(
        {"user_id": current_user.id}).skip(skip).limit(limit)
    expenses = await cursor.to_list(length=limit)
    return [Expense(**expense, id=str(expense["_id"])) for expense in expenses]


@router.put("/update-collection/{expense_id}")
async def update_collection(
    expense_id: str,
    updates: dict,
    db: DB,
    current_user: CurrentUser
):
    """
    Updates a specific expense by its ID.
    """
    try:
        # Ensure the expense belongs to the current user
        query = {"_id": ObjectId(expense_id), "user_id": current_user.id}
        update = {"$set": updates}

        result = await db.expenses.update_one(query, update)

        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found or unauthorized access"
            )

        return {"status": "success", "updated_count": result.modified_count}
    except Exception as err:
        print(f"Error updating collection: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update expense"
        )
