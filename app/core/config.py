"""
Core configuration for Enterprise Production Assistant
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # API Keys
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    ASTRA_DB_TOKEN: Optional[str] = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    ASTRA_DB_ENDPOINT: Optional[str] = os.getenv("ASTRA_DB_API_ENDPOINT")
    SERPER_API_KEY: Optional[str] = os.getenv("SERPER_API_KEY")
    
    # App settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    SUPPORTED_FORMATS: list = [".pdf"]
    SEARCH_TIMEOUT: int = 5
    CONFIDENCE_THRESHOLD: float = 0.3

settings = Settings()