from fastapi import APIRouter
from typing import Dict, Any
from backend.app.ml.model_registry import model_registry

router = APIRouter()

@router.get("/models")
def get_models() -> Dict[str, Any]:
    return model_registry.get_all_models()

@router.get("/models/status")
def get_models_status() -> Dict[str, Any]:
    return model_registry.get_model_status("b0_source_classifier")
