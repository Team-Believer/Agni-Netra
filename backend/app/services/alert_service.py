from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.database.repositories import AlertRepository
from backend.app.database.models import Alert

class AlertService:
    def __init__(self, db: Session):
        self.repo = AlertRepository(db)

    def get_active_alerts(self, limit: int = 20) -> List[Alert]:
        return self.repo.get_active(limit=limit)

    def create_alert(self, alert_data: Dict[str, Any]) -> Alert:
        return self.repo.create(alert_data)
