import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Agni-Netra"
    API_V1_STR: str = "/api"
    TAGLINE: str = "The satellite sees heat. Agni-Netra understands the event."
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/data/agni_netra.db")
    
    # Ingestion API keys (optional/demo fallback)
    FIRMS_API_KEY: str = os.getenv("FIRMS_API_KEY", "")
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    
    # Model config
    MODEL_DIR: str = os.getenv("MODEL_DIR", str(BASE_DIR / "models" / "b0"))
    MODEL_VERSION: str = "1.0.0"
    
    # Operational constants
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.65
    HIGH_RISK_THRESHOLD: float = 70.0
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
