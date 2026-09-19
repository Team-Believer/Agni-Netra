# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from backend.app.api.dependencies import get_db
from backend.app.services.event_service import EventService
from backend.app.services.alert_service import AlertService

router = APIRouter()

@router.get("/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    service = EventService(db)
    return service.get_kpi_summary()

@router.get("/dashboard/hotspots")
def get_dashboard_hotspots(db: Session = Depends(get_db)) -> Dict[str, Any]:
    service = EventService(db)
    events = service.get_events(limit=200)
    
    features = []
    for e in events:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [e.centroid_lon, e.centroid_lat]
            },
            "properties": {
                "event_id": e.event_id,
                "title": e.title,
                "location": e.location_name,
                "district": e.district,
                "classification": e.source_hypothesis,
                "confidence": e.confidence,
                "risk_index": e.risk_index,
                "risk_level": e.risk_level,
                "priority_level": e.priority_level,
                "verification_status": e.verification_status,
                "observation_count": e.observation_count,
                "last_observed": e.last_observed.isoformat() if e.last_observed else None
            }
        })
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

@router.get("/dashboard/alerts")
def get_dashboard_alerts(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    alert_service = AlertService(db)
    alerts = alert_service.get_active_alerts(limit=10)
    return [
        {
            "id": a.id,
            "event_id": a.event_id,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "title": a.title,
            "message": a.message,
            "created_at": a.created_at.isoformat() if a.created_at else None
        }
        for a in alerts
    ]
