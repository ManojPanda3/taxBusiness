import io
import google.generativeai as genai
from app.core.settings import settings  # Ensure this import is correct
from google.cloud import vision
from google.oauth2 import service_account
import logging
from google.ai.generativelanguage_v1beta.types import content
import json


class OCRService:
    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(
            settings.google_cloud_credentials
        )
        self.client = vision.ImageAnnotatorClient(credentials=credentials)
        # Initialize Gemini API
        # Use your API Key setting
        genai.configure(api_key=settings.gemini_api)
        self.generation_config = {
            "temperature": 0.1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_schema": content.Schema(
                type=content.Type.OBJECT,
                enum=[],
                required=["total_amount"],
                properties={
                    "total_amount": content.Schema(
                        type=content.Type.NUMBER,
                    ),
                    "date": content.Schema(
                        type=content.Type.STRING,
                    ),
                    "vendor": content.Schema(
                        type=content.Type.STRING,
                    ),
                    "items": content.Schema(
                        type=content.Type.ARRAY,
                        items=content.Schema(
                            type=content.Type.OBJECT,
                            enum=[],
                            required=["name", "price"],
                            properties={
                                "name": content.Schema(
                                    type=content.Type.STRING,
                                ),
                                "price": content.Schema(
                                    type=content.Type.NUMBER,
                                ),
                            },
                        ),
                    ),
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
            if response.full_text_annotation:
                texts = response.full_text_annotation.text
            else:
                return {"error": "No text found in image"}

            if not texts:
                return {"error": "No text found in image"}

            # Parse the extracted text to identify relevant fields
            extracted_data = await self._parse_receipt_text(texts)
            return extracted_data
        except Exception as e:
            logging.error(f"Error extracting receipt data: {e}")
            return {"error": "Failed to process image"}

    async def _parse_receipt_text(self, text: str) -> dict:
        """Parse extracted text using Gemini API to identify amount, date, vendor, etc."""
        prompt = f"""
        Extract the following information from the receipt text provided below.
        If the information is not found in the text return null.
        - total_amount: the total amount of the purchase, only return a number with 2 decimal places.
        - date: the date of the purchase in YYYY-MM-DD format.
        - vendor: the name of the store or vendor
        - items: a list of the items purchased, with their names and prices

        Receipt Text:
        {text}
        """
        try:
            response = self.model.generate_content(prompt)
            if response.text:
                try:
                    data = json.loads(response.text)
                    print(data)
                    return data
                except json.JSONDecodeError:
                    logging.error(
                        f"Gemini returned invalid json format: {response.text}"
                    )
                    return {"error": "Could not extract data from text"}
            else:
                logging.error(f"Gemini response: {response}")
                return {"error": "Could not extract data from text"}
        except Exception as e:
            logging.error(f"Error using Gemini API: {e}")
            return {"error": "Failed to process text with Gemini"}
