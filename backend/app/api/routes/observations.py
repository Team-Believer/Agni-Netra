from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.app.api.dependencies import get_db
from backend.app.database.models import Observation

router = APIRouter()

@router.get("/observations")
def list_observations(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    observations = db.query(Observation).order_by(Observation.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": o.id,
            "source": o.source,
            "source_observation_id": o.source_observation_id,
            "latitude": o.latitude,
            "longitude": o.longitude,
            "timestamp": o.timestamp.isoformat() if o.timestamp else None,
            "frp": o.frp,
            "brightness_temperature": o.brightness_temperature,
            "confidence": o.confidence,
            "satellite_sensor": o.satellite_sensor,
            "spatial_resolution": o.spatial_resolution,
            "quality": o.observation_quality
        }
        for o in observations
    ]

@router.get("/observations/{obs_id}")
def get_observation(obs_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    obs = db.query(Observation).filter(Observation.id == obs_id).first()
    if not obs:
        raise HTTPException(status_code=404, detail="Observation not found")
    return {
        "id": obs.id,
        "source": obs.source,
        "source_observation_id": obs.source_observation_id,
        "latitude": obs.latitude,
        "longitude": obs.longitude,
        "timestamp": obs.timestamp.isoformat() if obs.timestamp else None,
        "frp": obs.frp,
        "brightness_temperature": obs.brightness_temperature,
        "confidence": obs.confidence,
        "satellite_sensor": obs.satellite_sensor,
        "spatial_resolution": obs.spatial_resolution,
        "quality": obs.observation_quality,
        "raw_payload": obs.raw_payload
    }
