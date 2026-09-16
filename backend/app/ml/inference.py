import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

from backend.app.core.config import settings
from backend.app.core.logging import logger
from src.model.inference_b0 import AgniNetraB0Inference
from src.intelligence.analyze_event import analyze_event, EventIntelligenceResult

class ThermalEventInferenceService:
    def __init__(self):
        self.inference_engine: Optional[AgniNetraB0Inference] = None
        self._load_model()

    def _load_model(self):
        try:
            model_dir = settings.MODEL_DIR
            if os.path.exists(f"{model_dir}/xgboost_b0.json"):
                self.inference_engine = AgniNetraB0Inference(model_dir=model_dir)
                logger.info(f"Loaded XGBoost model from {model_dir}")
            else:
                logger.warning(f"Model file not found at {model_dir}/xgboost_b0.json. Inference will run in fallback/heuristic mode.")
        except Exception as e:
            logger.error(f"Failed to load XGBoost model: {e}")
            self.inference_engine = None

    def predict_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Runs inference directly against the XGBoost model artifact."""
        if self.inference_engine is None:
            return {
                "event_id": features.get("event_id", "UNKNOWN"),
                "classification": {
                    "label": "UNKNOWN",
                    "confidence": 0.0
                },
                "model_status": "MODEL_UNAVAILABLE",
                "top_3": []
            }
        try:
            raw_pred = self.inference_engine.predict_event(features)
            
            # Simulated Conformal Uncertainty & OOD layer (since real model is XGBoost without calibrated conformal wrapper yet)
            conf = raw_pred.get("classification", {}).get("confidence", 0.0)
            label = raw_pred.get("classification", {}).get("label", "UNKNOWN")
            
            # OOD (Out of Distribution) detection logic (mocked based on feature bounds)
            is_ood = features.get("max_frp", 0) > 1000 or features.get("max_frp", 0) < 0
            if is_ood:
                raw_pred["classification"]["label"] = "OOD"
                raw_pred["classification"]["confidence"] = 0.0
                raw_pred["prediction_set"] = []
                raw_pred["uncertainty"] = 1.0
                raw_pred["ood_status"] = True
                return raw_pred

            # Conformal Prediction Set (if confidence is low, output multiple potential classes)
            if conf < 0.65:
                raw_pred["prediction_set"] = [label, "Unknown Anomaly", "Routine Flare"]
                raw_pred["uncertainty"] = round(1.0 - conf, 2)
                # Refuse forced classification if very low confidence
                if conf < 0.40:
                    raw_pred["classification"]["label"] = "UNKNOWN / NEEDS VERIFICATION"
            else:
                raw_pred["prediction_set"] = [label]
                raw_pred["uncertainty"] = round(1.0 - conf, 2)
            
            raw_pred["ood_status"] = False
            return raw_pred

        except Exception as e:
            logger.error(f"Prediction failed for event {features.get('event_id')}: {e}")
            return {
                "event_id": features.get("event_id", "UNKNOWN"),
                "classification": {
                    "label": "UNKNOWN",
                    "confidence": 0.0
                },
                "model_status": f"ERROR: {str(e)}",
                "prediction_set": [],
                "uncertainty": 1.0,
                "ood_status": False,
                "top_3": []
            }

    def run_full_intelligence(self, raw_event: Dict[str, Any]) -> EventIntelligenceResult:
        """
        Runs the full 13-stage Agni-Netra Unified Production Intelligence pipeline (analyze_event).
        Returns the canonical EventIntelligenceResult dataclass.
        """
        return analyze_event(raw_event)

inference_service = ThermalEventInferenceService()
