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
    
    # Auth / Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "AGNI_NETRA_LOCAL_INSECURE_SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    AUTH_DEV_USERNAME: str = os.getenv("AUTH_DEV_USERNAME", "Dax")
    AUTH_DEV_PASSWORD: str = os.getenv("AUTH_DEV_PASSWORD", "Dax@1707")
    
    class Config:
        case_sensitive = True
        env_file = str(BASE_DIR / "backend" / ".env")

settings = Settings()
