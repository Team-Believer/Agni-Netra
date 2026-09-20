from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import Dict, Any

from backend.app.api.dependencies import get_db
from backend.app.services.report_service import ReportService

router = APIRouter()

@router.get("/reports/{event_id}")
def get_event_report(event_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    service = ReportService(db)
    report = service.generate_event_report(event_id)
    if not report:
        raise HTTPException(status_code=404, detail="Event not found")
    return report

@router.get("/reports/export/csv")
def export_reports_csv(db: Session = Depends(get_db)):
    service = ReportService(db)
    csv_data = service.export_events_csv()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=agni_netra_events_export.csv"}
    )

@router.get("/reports/export/{event_id}/pdf")
def export_report_pdf(event_id: str, db: Session = Depends(get_db)):
    service = ReportService(db)
    pdf_bytes = service.generate_event_pdf(event_id)
    if not pdf_bytes:
        raise HTTPException(status_code=404, detail="Event not found or PDF generation failed")
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report_{event_id}.pdf"}
    )
