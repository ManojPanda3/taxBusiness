import logging


class OCRService:
    def _init_(self):
        credentials = service_account.Credentials.from_service_account_file(
            settings.google_cloud_credentials)
        self.client = vision.ImageAnnotatorClient(credentials=credentials)

    async def extract_receipt_data(self, image_content: bytes) -> dict:
        """Extract text from receipt images using Google Cloud Vision API."""
        try:
            image = vision.Image(content=image_content)
            response = self.client.text_detection(image=image)
            texts = response.text_annotations

            if not texts:
                return {"error": "No text found in image"}

            # Parse the extracted text to identify relevant fields
            extracted_data = self._parse_receipt_text(texts[0].description)
            return extracted_data
        except Exception as e:
            logging.error(f"Error extracting receipt data: {e}")
            return {"error": "Failed to process image"}

    def _parse_receipt_text(self, text: str) -> dict:
        """Parse extracted text to identify amount, date, vendor, etc."""
        import re  # Ensure regex module is imported

        lines = text.split('\n')
        data = {
            "total_amount": None,
            "date": None,
            "vendor": None,
            "items": []
        }

        for line in lines:
            # Extract amounts using regex
            amount_match = re.search(r'\$\d+(\.\d{2})?', line)
            if amount_match:
                data['total_amount'] = amount_match.group()

            # Extract dates using regex
            date_match = re.search(r'\b\d{2}/\d{2}/\d{4}\b', line)
            if date_match:
                data['date'] = date_match.group()

            # Example logic to identify vendor, can be more complex
            if "vendor" in line.lower():
                data['vendor'] = line.split(':')[-1].strip()

        return data
