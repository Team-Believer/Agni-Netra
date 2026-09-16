from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import datetime

from backend.app.database.models import (
    Event, Observation, EventObservation, EventEvidence,
    EventPrediction, VerificationRecord, Alert, DataSource, AuditLog
)

class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Event]:
        query = self.db.query(Event)
        if status and status != "All":
            query = query.filter(Event.verification_status == status)
        if priority and priority != "All":
            query = query.filter(Event.priority_level == priority)
        if search:
            search_fmt = f"%{search}%"
            query = query.filter(
                (Event.event_id.ilike(search_fmt)) |
                (Event.title.ilike(search_fmt)) |
                (Event.location_name.ilike(search_fmt)) |
                (Event.district.ilike(search_fmt)) |
                (Event.nearby_facility.ilike(search_fmt))
            )
        return query.order_by(desc(Event.last_observed)).offset(skip).limit(limit).all()

    def get_by_event_id(self, event_id: str) -> Optional[Event]:
        return self.db.query(Event).filter(Event.event_id == event_id).first()

    def create(self, event_data: Dict[str, Any]) -> Event:
        event = Event(**event_data)
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def update(self, event: Event, update_data: Dict[str, Any]) -> Event:
        for key, value in update_data.items():
            setattr(event, key, value)
        event.updated_at = datetime.datetime.utcnow()
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_kpi_summary(self) -> Dict[str, Any]:
        total_active = self.db.query(func.count(Event.id)).filter(
            Event.current_state.in_(["Active", "Escalating", "Persistent", "Emerging", "Detected"])
        ).scalar() or 0

        high_priority = self.db.query(func.count(Event.id)).filter(
            Event.priority_level.in_(["Critical", "High"])
        ).scalar() or 0

        under_verification = self.db.query(func.count(Event.id)).filter(
            Event.verification_status.in_(["Needs Verification", "Under Verification", "Needs More Evidence"])
        ).scalar() or 0

        resolved_24h = self.db.query(func.count(Event.id)).filter(
            Event.current_state == "Resolved"
        ).scalar() or 0

        total_events = self.db.query(func.count(Event.id)).scalar() or 0

        return {
            "total_active": total_active,
            "high_priority": high_priority,
            "under_verification": under_verification,
            "resolved_24h": resolved_24h,
            "total_events": total_events,
            "active_change_vs_yesterday": 0,
            "high_priority_change": 0,
            "under_verification_change": 0,
            "resolved_change": 0,
            "system_status": "System Operational",
            "last_synced": datetime.datetime.utcnow().isoformat()
        }


class ObservationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, obs_id: int) -> Optional[Observation]:
        return self.db.query(Observation).filter(Observation.id == obs_id).first()

    def get_for_event(self, event_id: str) -> List[Observation]:
        return (
            self.db.query(Observation)
            .join(EventObservation, Observation.id == EventObservation.observation_id)
            .filter(EventObservation.event_id == event_id)
            .order_by(Observation.timestamp.asc())
            .all()
        )

    def create(self, obs_data: Dict[str, Any]) -> Observation:
        obs = Observation(**obs_data)
        self.db.add(obs)
        self.db.commit()
        self.db.refresh(obs)
        return obs


class VerificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_record(
        self,
        event_id: str,
        reviewer: str,
        decision: str,
        comment: Optional[str],
        previous_status: Optional[str],
        new_status: str
    ) -> VerificationRecord:
        record = VerificationRecord(
            event_id=event_id,
            reviewer=reviewer,
            decision=decision,
            comment=comment,
            previous_status=previous_status,
            new_status=new_status,
            timestamp=datetime.datetime.utcnow()
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_for_event(self, event_id: str) -> List[VerificationRecord]:
        return (
            self.db.query(VerificationRecord)
            .filter(VerificationRecord.event_id == event_id)
            .order_by(desc(VerificationRecord.timestamp))
            .all()
        )


class AlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active(self, limit: int = 20) -> List[Alert]:
        return (
            self.db.query(Alert)
            .filter(Alert.status == "Active")
            .order_by(desc(Alert.created_at))
            .limit(limit)
            .all()
        )

    def create(self, alert_data: Dict[str, Any]) -> Alert:
        alert = Alert(**alert_data)
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert


class DataSourceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[DataSource]:
        return self.db.query(DataSource).all()


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def log_action(
        self,
        actor: str,
        action: str,
        entity_type: str,
        entity_id: str,
        previous_state: Optional[str] = None,
        new_state: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        log_entry = AuditLog(
            actor=actor,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            previous_state=previous_state,
            new_state=new_state,
            details=details,
            timestamp=datetime.datetime.utcnow()
        )
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        return log_entry
