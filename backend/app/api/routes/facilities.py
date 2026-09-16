from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List

from backend.app.api.dependencies import get_db
from backend.app.database.models import Event

router = APIRouter()

@router.get("/facilities")
def get_facilities(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    # Extract unique facilities from events
    query = db.query(
        Event.nearby_facility,
        Event.facility_type,
        Event.location_name,
        func.count(Event.id).label('event_count'),
        func.max(Event.last_observed).label('last_active')
    ).filter(Event.nearby_facility != None, Event.nearby_facility != '').group_by(
        Event.nearby_facility, Event.facility_type, Event.location_name
    ).all()
    
    return [
        {
            "id": row.nearby_facility.replace(" ", "_").lower(),
            "name": row.nearby_facility,
            "type": row.facility_type or 'Unknown',
            "location": row.location_name or 'Unknown',
            "event_count": row.event_count,
            "last_active": row.last_active.isoformat() if row.last_active else None
        }
        for row in query
    ]

@router.get("/facilities/{facility_id}")
def get_facility_details(facility_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    # Reverse the ID back to name approximately (or fetch all and match)
    facilities = get_facilities(db)
    facility = next((f for f in facilities if f["id"] == facility_id), None)
    
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found in active events.")
        
    # Get associated events
    events = db.query(Event).filter(Event.nearby_facility == facility["name"]).all()
    
    facility["events"] = [
        {
            "event_id": e.event_id,
            "title": e.title,
            "priority": e.priority_level,
            "status": e.verification_status,
            "last_seen": e.last_observed.isoformat() if e.last_observed else None
        }
        for e in events
    ]
    
    return facility
