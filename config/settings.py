"""
Production Configuration Settings
Centralizes all application configuration
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Production application settings"""
    
    # Application
    APP_NAME = "production-rag-app"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # Database
    ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
    ASTRA_DB_KEYSPACE = os.getenv("ASTRA_DB_KEYSPACE", "default_keyspace")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "semantic_data")
    
    # AI Services
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    
    # Search APIs
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")
    
    # Embedding
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", 1536))
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    
    # Memory
    MAX_CONVERSATION_TURNS = int(os.getenv("MAX_CONVERSATION_TURNS", 5))
    CONVERSATION_TIMEOUT_HOURS = int(os.getenv("CONVERSATION_TIMEOUT_HOURS", 24))
    
    # Content Moderation
    ENABLE_MODERATION = os.getenv("ENABLE_MODERATION", "true").lower() == "true"
    
    # Performance
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 100))
    REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", 30))

# Global settings instance
settings = Settings()

def get_settings():
    """Get application settings"""
    return settings