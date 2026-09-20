from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List

from backend.app.api.dependencies import get_db
from backend.app.database.models import Event, Facility

router = APIRouter()

@router.get("/facilities")
def get_facilities(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    # Join Facility with Event to get event counts
    query = db.query(
        Facility.facility_id,
        Facility.facility_name,
        Facility.category,
        Facility.state,
        Facility.district,
        func.count(Event.id).label('event_count')
    ).outerjoin(
        Event, Event.nearby_facility == Facility.facility_name
    ).group_by(
        Facility.facility_id, Facility.facility_name, Facility.category, Facility.state, Facility.district
    ).all()
    
    return [
        {
            "id": row.facility_id,
            "name": row.facility_name,
            "type": row.category or 'Unknown',
            "location": f"{row.district}, {row.state}" if row.district and row.state else 'Unknown',
            "event_count": row.event_count,
        }
        for row in query
    ]

@router.get("/facilities/{facility_id}")
def get_facility_details(facility_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    facility = db.query(Facility).filter(Facility.facility_id == facility_id).first()
    
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found.")
        
    # Get associated events
    events = db.query(Event).filter(Event.nearby_facility == facility.facility_name).all()
    
    return {
        "id": facility.facility_id,
        "name": facility.facility_name,
        "type": facility.category,
        "location": f"{facility.district}, {facility.state}",
        "latitude": facility.latitude,
        "longitude": facility.longitude,
        "description": facility.description,
        "contact_name": facility.contact_name,
        "contact_role": facility.contact_role,
        "contact_number": facility.contact_number,
        "event_count": len(events),
        "events": [
            {
                "event_id": e.event_id,
                "title": e.title,
                "priority": e.priority_level,
                "status": e.verification_status,
                "last_seen": e.last_observed.isoformat() if e.last_observed else None
            }
            for e in events
        ]
    }
