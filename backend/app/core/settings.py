# backend/app/core/settings.py
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
load_dotenv()


class Settings(BaseSettings):
    mongodb_uri: str = os.getenv("MONGODB_URI")
    jwt_secret: str = os.getenv("JWT_SECRET")
    google_cloud_credentials: str = os.getenv("GOOGLE_CLOUD_CREDENTIALS")
    taxjar_api_key: str = os.getenv("TAXJAR_API_KEY")
    gemini_api: str = os.getenv("GEMINI_API")

    class Config:
        env_file = ".env"


settings = Settings()
