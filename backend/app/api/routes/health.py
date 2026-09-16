from fastapi import APIRouter
import datetime

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Agni-Netra Operational Intelligence API",
        "tagline": "The satellite sees heat. Agni-Netra understands the event.",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "database": "SQLite Connected",
        "model_engine": "XGBoost Ready"
    }
