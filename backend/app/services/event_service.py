from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.database.repositories import EventRepository, ObservationRepository
from backend.app.database.models import Event

class EventService:
    def __init__(self, db: Session):
        self.repo = EventRepository(db)
        self.obs_repo = ObservationRepository(db)

    def get_events(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Event]:
        return self.repo.get_all(skip=skip, limit=limit, status=status, priority=priority, search=search)

    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        return self.repo.get_by_event_id(event_id)

    def get_event_timeline(self, event_id: str) -> List[Dict[str, Any]]:
        observations = self.obs_repo.get_for_event(event_id)
        timeline = []
        for obs in observations:
            timeline.append({
                "timestamp": obs.timestamp.isoformat() if obs.timestamp else None,
                "satellite": obs.satellite_sensor,
                "frp": obs.frp,
                "brightness_temperature": obs.brightness_temperature,
                "confidence": obs.confidence,
                "quality": obs.observation_quality
            })
        return timeline

    def get_kpi_summary(self) -> Dict[str, Any]:
        return self.repo.get_kpi_summary()
