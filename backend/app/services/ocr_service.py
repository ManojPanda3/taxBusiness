import io
import json
import logging
from google.cloud import vision
from google.oauth2 import service_account
import google.generativeai as genai
from app.core.settings import settings  # Ensure this import is correct
from google.ai.generativelanguage_v1beta.types import content


class OCRService:
    def __init__(self):
        # Initialize Google Cloud Vision API Client
        credentials = service_account.Credentials.from_service_account_file(
            settings.google_cloud_credentials
        )
        self.client = vision.ImageAnnotatorClient(credentials=credentials)

        # Initialize Gemini API
        genai.configure(api_key=settings.gemini_api)
        self.generation_config = {
            "temperature": 0.1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_schema": content.Schema(
                type=content.Type.OBJECT,
                required=["total_amount", "date", "vendor", "items"],
                properties={
                    "total_amount": content.Schema(type=content.Type.NUMBER),
                    "date": content.Schema(type=content.Type.STRING),
                    "vendor": content.Schema(type=content.Type.STRING),
                    "invoice_number": content.Schema(type=content.Type.STRING),
                    "tax_rate": content.Schema(type=content.Type.NUMBER),
                    "tax_amount": content.Schema(type=content.Type.NUMBER),
                    "items": content.Schema(
                        type=content.Type.ARRAY,
                        items=content.Schema(
                            type=content.Type.OBJECT,
                            required=["name", "price", "quantity"],
                            properties={
                                "name": content.Schema(type=content.Type.STRING),
                                "price": content.Schema(type=content.Type.NUMBER),
                                "quantity": content.Schema(type=content.Type.NUMBER),
                            },
                        ),
                    ),
                    "payment_method": content.Schema(type=content.Type.STRING),
                    "business_purpose": content.Schema(type=content.Type.STRING),
                },
            ),
            "response_mime_type": "application/json",
        }
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config=self.generation_config,
        )

    async def extract_receipt_data(self, image_content: bytes) -> dict:
        """Extract text from receipt images using Google Cloud Vision API."""
        try:
            image = vision.Image(content=image_content)
            response = self.client.text_detection(image=image)
            
            if not response.full_text_annotation or not response.full_text_annotation.text:
                return {"error": "No text found in image"}

            extracted_text = response.full_text_annotation.text
            extracted_data = await self._parse_receipt_text(extracted_text)
            return extracted_data
        except Exception as e:
            logging.error(f"Error extracting receipt data: {e}")
            return {"error": "Failed to process image"}

    async def _parse_receipt_text(self, text: str) -> dict:
        """Parse extracted text using Gemini API to identify amount, date, vendor, etc."""
        prompt = f"""
        Extract the following information from the receipt text provided below.
        If the information is not found in the text, return null.
        - total_amount: The total amount of the transaction (number with 2 decimal places).
        - date: The date of the transaction in YYYY-MM-DD format.
        - vendor: The name of the vendor or store.
        - invoice_number: The invoice number, if available.
        - tax_rate: The applicable tax rate (percentage).
        - tax_amount: The total tax amount applied to the transaction.
        - items: A list of purchased items, with the following details:
          - name: Name of the item.
          - price: Price of the item (number with 2 decimal places).
          - quantity: Quantity of the item purchased.
        - payment_method: The payment method used (if available).
        - business_purpose: A brief description of the business purpose.

        Receipt Text:
        {text}
        """
        try:
            response = self.model.generate_content(prompt)
            if response.text:
                try:
                    data = json.loads(response.text)
                    return data
                except json.JSONDecodeError:
                    logging.error(f"Gemini returned invalid JSON format: {response.text}")
                    return {"error": "Could not extract data from text"}
            else:
                logging.error(f"Gemini response: {response}")
                return {"error": "Could not extract data from text"}
        except Exception as e:
            logging.error(f"Error using Gemini API: {e}")
            return {"error": "Failed to process text with Gemini"}
