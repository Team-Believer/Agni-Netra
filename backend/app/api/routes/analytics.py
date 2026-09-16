from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
import datetime

from backend.app.api.dependencies import get_db
from backend.app.database.models import Event

router = APIRouter()

@router.get("/analytics/events-over-time")
def get_events_over_time(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    # SQLite friendly date truncation
    query = db.query(
        func.date(Event.first_detected).label('date'),
        func.count(Event.id).label('count')
    ).group_by(func.date(Event.first_detected)).order_by('date').all()
    
    return [{"date": row.date, "count": row.count} for row in query if row.date]

@router.get("/analytics/classifications")
def get_events_by_classification(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    query = db.query(
        Event.source_hypothesis.label('classification'),
        func.count(Event.id).label('count')
    ).group_by(Event.source_hypothesis).all()
    
    return [{"classification": row.classification or 'Unknown', "count": row.count} for row in query]

@router.get("/analytics/priorities")
def get_events_by_priority(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    query = db.query(
        Event.priority_level.label('priority'),
        func.count(Event.id).label('count')
    ).group_by(Event.priority_level).all()
    
    return [{"priority": row.priority or 'Monitor', "count": row.count} for row in query]

@router.get("/analytics/status")
def get_events_by_status(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    query = db.query(
        Event.verification_status.label('status'),
        func.count(Event.id).label('count')
    ).group_by(Event.verification_status).all()
    
    return [{"status": row.status or 'Unknown', "count": row.count} for row in query]
