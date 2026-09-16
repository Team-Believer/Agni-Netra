from typing import List, Dict, Any, Optional
import io
import csv
import json
import datetime
from sqlalchemy.orm import Session
from backend.app.database.repositories import EventRepository
from backend.app.database.models import Event

class ReportService:
    def __init__(self, db: Session):
        self.repo = EventRepository(db)

    def generate_event_report(self, event_id: str) -> Optional[Dict[str, Any]]:
        event = self.repo.get_by_event_id(event_id)
        if not event:
            return None

        evidence_items = [
            {
                "source": ev.source,
                "type": ev.evidence_type,
                "direction": ev.direction,
                "value": ev.value,
                "explanation": ev.explanation
            }
            for ev in event.evidence_items
        ]

        return {
            "report_id": f"RPT-{event.event_id}-{int(datetime.datetime.utcnow().timestamp())}",
            "generated_at": datetime.datetime.utcnow().isoformat(),
            "event_id": event.event_id,
            "title": event.title,
            "location": event.location_name,
            "district": event.district,
            "state": event.state,
            "coordinates": {
                "latitude": event.centroid_lat,
                "longitude": event.centroid_lon
            },
            "timeline": {
                "first_detected": event.first_detected.isoformat() if event.first_detected else None,
                "last_observed": event.last_observed.isoformat() if event.last_observed else None,
                "observation_count": event.observation_count
            },
            "ai_intelligence": {
                "source_hypothesis": event.source_hypothesis,
                "confidence": event.confidence,
                "behavior": event.behavior,
                "abnormality": event.abnormality,
                "risk_index": event.risk_index,
                "risk_level": event.risk_level,
                "priority_level": event.priority_level,
                "evidence_completeness": event.evidence_completeness,
                "current_assessment": event.current_assessment
            },
            "explanations": {
                "why": event.why_explanation,
                "why_not": event.why_not_explanation,
                "what_changed": event.what_changed_explanation
            },
            "evidence": evidence_items,
            "verification_status": event.verification_status
        }

    def export_events_csv(self) -> str:
        events = self.repo.get_all(limit=500)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Event ID", "Title", "Location", "Latitude", "Longitude",
            "Classification", "Confidence", "Behavior", "Abnormality",
            "Risk Index", "Priority", "Status", "First Seen", "Last Seen", "Observations"
        ])
        for e in events:
            writer.writerow([
                e.event_id, e.title, e.location_name, e.centroid_lat, e.centroid_lon,
                e.source_hypothesis, e.confidence, e.behavior, e.abnormality,
                e.risk_index, e.priority_level, e.verification_status,
                e.first_detected, e.last_observed, e.observation_count
            ])
        return output.getvalue()
