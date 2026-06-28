from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    ALPHA_VANTAGE_API_KEY: str
    MODEL_NAME: str = "gemini-2.5-flash"
    FALLBACK_MODEL_NAME: str = "gemini-1.5-flash"
    CHROMA_DIR: str = "chroma_db"
    DOCS_DIR: str = "documents"
    ALPHA_VANTAGE_BASE_URL: str = "https://www.alphavantage.co/query"
    
    # Security / Operations
    ALLOWED_ORIGINS: List[str] = ["*"]
    RATE_LIMIT_STRING: str = "10/minute"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Backward compatibility exports
GOOGLE_API_KEY = settings.GOOGLE_API_KEY
ALPHA_VANTAGE_API_KEY = settings.ALPHA_VANTAGE_API_KEY
CHROMA_DIR = settings.CHROMA_DIR
DOCS_DIR = settings.DOCS_DIR
MODEL_NAME = settings.MODEL_NAME
ALPHA_VANTAGE_BASE_URL = settings.ALPHA_VANTAGE_BASE_URL