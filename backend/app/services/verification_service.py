from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.database.repositories import EventRepository, VerificationRepository, AuditLogRepository
from backend.app.database.models import VerificationRecord, Event

class VerificationService:
    def __init__(self, db: Session):
        self.db = db
        self.event_repo = EventRepository(db)
        self.verif_repo = VerificationRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def verify_event(
        self,
        event_id: str,
        reviewer: str,
        decision: str,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        event = self.event_repo.get_by_event_id(event_id)
        if not event:
            return {"success": False, "error": f"Event {event_id} not found."}

        prev_status = event.verification_status
        
        # Decision mapping:
        # confirmed -> Confirmed
        # rejected / false_alarm -> Rejected
        # needs_data -> Needs More Evidence
        # monitoring -> Monitoring
        decision_clean = decision.lower()
        if decision_clean in ["confirmed", "confirm"]:
            new_status = "Confirmed"
        elif decision_clean in ["rejected", "reject", "false_alarm"]:
            new_status = "Rejected"
        elif decision_clean in ["needs_more_evidence", "needs_data", "request_more_data"]:
            new_status = "Needs More Evidence"
        elif decision_clean in ["monitoring", "monitor"]:
            new_status = "Monitoring"
        else:
            new_status = "Analyst Reviewed"

        # Update event record
        self.event_repo.update(event, {"verification_status": new_status})

        # Insert verification audit record
        record = self.verif_repo.add_record(
            event_id=event_id,
            reviewer=reviewer,
            decision=decision,
            comment=comment,
            previous_status=prev_status,
            new_status=new_status
        )

        # Insert general system audit log
        self.audit_repo.log_action(
            actor=reviewer,
            action="VERIFY_EVENT",
            entity_type="Event",
            entity_id=event_id,
            previous_state=prev_status,
            new_state=new_status,
            details={"decision": decision, "comment": comment}
        )

        return {
            "success": True,
            "event_id": event_id,
            "previous_status": prev_status,
            "new_status": new_status,
            "reviewer": reviewer,
            "timestamp": record.timestamp.isoformat()
        }
