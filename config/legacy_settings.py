"""Application configuration following industry standards."""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class DatabaseConfig:
    """AstraDB configuration settings."""
    
    token: str
    api_endpoint: str
    collection_name: str = "semantic_data"
    keyspace: str = "default_keyspace"
    
    def __post_init__(self) -> None:
        if not self.token:
            raise ValueError("ASTRA_DB_APPLICATION_TOKEN is required")
        if not self.api_endpoint:
            raise ValueError("ASTRA_DB_API_ENDPOINT is required")


@dataclass(frozen=True)
class ProcessingConfig:
    """Document processing configuration."""
    
    data_folder: Path
    chunk_size: int = 800
    chunk_overlap: int = 150
    min_chunk_size: int = 50
    supported_extensions: frozenset = frozenset({
        ".pdf", ".txt", ".docx", ".json", ".csv", ".md"
    })
    
    def __post_init__(self) -> None:
        if not self.data_folder.exists():
            raise FileNotFoundError(f"Data folder not found: {self.data_folder}")


@dataclass(frozen=True)
class APIConfig:
    """External API configuration."""
    
    groq_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None


class Settings:
    """Application settings manager."""
    
    def __init__(self) -> None:
        self._database = self._load_database_config()
        self._processing = self._load_processing_config()
        self._api = self._load_api_config()
    
    @property
    def database(self) -> DatabaseConfig:
        return self._database
    
    @property
    def processing(self) -> ProcessingConfig:
        return self._processing
    
    @property
    def api(self) -> APIConfig:
        return self._api
    
    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration from environment."""
        return DatabaseConfig(
            token=os.getenv("ASTRA_DB_APPLICATION_TOKEN", ""),
            api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT", ""),
            collection_name=os.getenv("COLLECTION_NAME", "semantic_data"),
            keyspace=os.getenv("ASTRA_DB_KEYSPACE", "default_keyspace")
        )
    
    def _load_processing_config(self) -> ProcessingConfig:
        """Load processing configuration from environment."""
        data_folder = Path(os.getenv("DATA_FOLDER", str(PROJECT_ROOT / "data")))
        
        return ProcessingConfig(
            data_folder=data_folder,
            chunk_size=int(os.getenv("CHUNK_SIZE", "800")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "150")),
            min_chunk_size=int(os.getenv("MIN_CHUNK_SIZE", "50"))
        )
    
    def _load_api_config(self) -> APIConfig:
        """Load API configuration from environment."""
        return APIConfig(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )


# Global settings instance
settings = Settings()
