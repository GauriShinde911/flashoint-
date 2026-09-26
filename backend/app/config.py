import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    project_name: str = "Development Priority Intelligence"
    environment: str = os.getenv("ENVIRONMENT", "development")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    default_country: str = os.getenv("DEFAULT_COUNTRY", "IND")
    cors_origins: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000,http://127.0.0.1:5500,http://localhost:5500,https://render.com,https://web.app,https://firebaseapp.com"
        ).split(",")
        if origin.strip()
    ]

settings = Settings()

