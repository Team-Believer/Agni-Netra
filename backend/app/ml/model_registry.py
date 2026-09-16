from typing import Dict, Any, Optional
import os
import json
from pathlib import Path

from backend.app.core.config import settings
from backend.app.core.logging import logger

class ModelRegistry:
    def __init__(self):
        self.models_meta: Dict[str, Dict[str, Any]] = {}
        self._load_registry()

    def _load_registry(self):
        model_dir = Path(settings.MODEL_DIR)
        config_path = model_dir / "model_config.json"
        
        status = "UNAVAILABLE"
        features = []
        model_type = "XGBoost"
        
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    cfg = json.load(f)
                    model_type = cfg.get("model_type", "XGBoost")
                    features = cfg.get("features", [])
                    status = "READY"
            except Exception as e:
                logger.error(f"Error reading model config: {e}")
                status = "ERROR"

        self.models_meta["b0_source_classifier"] = {
            "name": "Agni-Netra B0 Thermal Source Classifier",
            "model_version": settings.MODEL_VERSION,
            "model_type": model_type,
            "status": status,
            "feature_count": len(features),
            "features": features,
            "classes": [
                "Industrial Fire",
                "Routine Flare",
                "Abnormal/Emergency Flare",
                "Agricultural Burn",
                "Wildfire",
                "Mining/Industrial Heat",
                "Landfill/Other",
                "Unknown"
            ],
            "schema_version": "AGN-EVENT-INTELLIGENCE-1.0",
            "pipeline_version": "1.0.0"
        }

    def get_model_status(self, model_key: str = "b0_source_classifier") -> Dict[str, Any]:
        return self.models_meta.get(model_key, {"status": "UNKNOWN"})

    def get_all_models(self) -> Dict[str, Any]:
        return self.models_meta

model_registry = ModelRegistry()
