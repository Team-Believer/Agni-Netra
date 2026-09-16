from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.app.api.dependencies import get_db
from backend.app.services.alert_service import AlertService

router = APIRouter()

@router.get("/alerts")
def get_alerts(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    service = AlertService(db)
    alerts = service.get_active_alerts(limit=limit)
    return [
        {
            "id": a.id,
            "event_id": a.event_id,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "title": a.title,
            "message": a.message,
            "status": a.status,
            "created_at": a.created_at.isoformat() if a.created_at else None
        }
        for a in alerts
    ]
