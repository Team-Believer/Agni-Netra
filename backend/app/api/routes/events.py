from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from backend.app.api.dependencies import get_db
from backend.app.services.event_service import EventService
from backend.app.services.verification_service import VerificationService

router = APIRouter()

class VerificationPayload(BaseModel):
    decision: str # "confirmed", "rejected", "needs_more_evidence", "monitoring"
    comment: Optional[str] = None
    reviewer: str = "Ananya Sharma"

@router.get("/events")
def list_events(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    service = EventService(db)
    events = service.get_events(skip=skip, limit=limit, status=status, priority=priority, search=search)
    
    return [
        {
            "id": e.id,
            "event_id": e.event_id,
            "title": e.title,
            "location": e.location_name,
            "district": e.district,
            "state": e.state,
            "nearby_facility": e.nearby_facility,
            "latitude": e.centroid_lat,
            "longitude": e.centroid_lon,
            "classification": e.source_hypothesis,
            "confidence": e.confidence,
            "evidence_completeness": e.evidence_completeness,
            "risk_index": e.risk_index,
            "risk_level": e.risk_level,
            "priority": e.priority_level,
            "status": e.verification_status,
            "behavior": e.behavior,
            "abnormality": e.abnormality,
            "first_seen": e.first_detected.isoformat() if e.first_detected else None,
            "last_seen": e.last_observed.isoformat() if e.last_observed else None,
            "observations_count": e.observation_count,
            "frp_change_pct": e.frp_change_pct,
            "footprint_expansion_factor": e.footprint_expansion_factor,
            "current_assessment": e.current_assessment,
            "satellite_image_url": e.satellite_image_url
        }
        for e in events
    ]

@router.get("/events/{event_id}")
def get_event_detail(event_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    service = EventService(db)
    event = service.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found")

    evidence_items = [
        {
            "id": ev.id,
            "source": ev.source,
            "sensor": ev.sensor,
            "availability": ev.availability,
            "evidence_type": ev.evidence_type,
            "direction": ev.direction,
            "quality": ev.quality,
            "relevance": ev.relevance,
            "value": ev.value,
            "explanation": ev.explanation
        }
        for ev in event.evidence_items
    ]

    verifications = [
        {
            "reviewer": v.reviewer,
            "decision": v.decision,
            "comment": v.comment,
            "new_status": v.new_status,
            "timestamp": v.timestamp.isoformat() if v.timestamp else None
        }
        for v in event.verifications
    ]

    return {
        "event_id": event.event_id,
        "title": event.title,
        "location": event.location_name,
        "district": event.district,
        "state": event.state,
        "nearby_facility": event.nearby_facility,
        "facility_type": event.facility_type,
        "latitude": event.centroid_lat,
        "longitude": event.centroid_lon,
        "bounding_geojson": event.bounding_geojson,
        "first_seen": event.first_detected.isoformat() if event.first_detected else None,
        "last_seen": event.last_observed.isoformat() if event.last_observed else None,
        "observations_count": event.observation_count,
        "classification": event.source_hypothesis,
        "confidence": event.confidence,
        "evidence_completeness": event.evidence_completeness,
        "risk_index": event.risk_index,
        "risk_level": event.risk_level,
        "priority": event.priority_level,
        "status": event.verification_status,
        "behavior": event.behavior,
        "abnormality": event.abnormality,
        "frp_change_pct": event.frp_change_pct,
        "footprint_expansion_factor": event.footprint_expansion_factor,
        "current_assessment": event.current_assessment,
        "satellite_image_url": event.satellite_image_url,
        "explanations": {
            "why": event.why_explanation or [],
            "why_not": event.why_not_explanation or [],
            "what_changed": event.what_changed_explanation or []
        },
        "evidence": evidence_items,
        "verifications": verifications,
        "predictions": [
            {
                "model_name": p.model_name,
                "predicted_class": p.predicted_class,
                "confidence": p.confidence,
                "prediction_set": p.prediction_set,
                "uncertainty": p.uncertainty,
                "ood_status": p.ood_status
            }
            for p in event.predictions
        ] if hasattr(event, 'predictions') else []
    }

@router.get("/events/{event_id}/timeline")
def get_event_timeline(event_id: str, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    service = EventService(db)
    return service.get_event_timeline(event_id)

@router.get("/events/{event_id}/evidence")
def get_event_evidence(event_id: str, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    service = EventService(db)
    event = service.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return [
        {
            "id": ev.id,
            "source": ev.source,
            "sensor": ev.sensor,
            "availability": ev.availability,
            "evidence_type": ev.evidence_type,
            "direction": ev.direction,
            "quality": ev.quality,
            "relevance": ev.relevance,
            "value": ev.value,
            "explanation": ev.explanation
        }
        for ev in event.evidence_items
    ]

@router.post("/events/{event_id}/verify")
def verify_event(
    event_id: str,
    payload: VerificationPayload,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    verif_service = VerificationService(db)
    result = verif_service.verify_event(
        event_id=event_id,
        reviewer=payload.reviewer,
        decision=payload.decision,
        comment=payload.comment
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result
