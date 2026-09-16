from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.app.api.dependencies import get_db
from backend.app.database.repositories import DataSourceRepository

router = APIRouter()

@router.get("/sources")
def get_sources(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    repo = DataSourceRepository(db)
    sources = repo.get_all()
    if not sources:
        return []
    return [
        {
            "name": s.name,
            "source_type": s.source_type,
            "status": s.status,
            "coverage": s.coverage,
            "latency_ms": s.latency_ms,
            "record_count": s.record_count,
            "last_sync": s.last_sync.isoformat() if s.last_sync else None
        }
        for s in sources
    ]

@router.get("/sources/status")
def get_sources_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    sources = get_sources(db)
    online_count = sum(1 for s in sources if s.get("status") == "ONLINE")
    return {
        "total_sources": len(sources),
        "online_sources": online_count,
        "ratio": f"{online_count}/{len(sources)}",
        "system_health": "OPTIMAL" if online_count >= 6 else "DEGRADED"
    }
