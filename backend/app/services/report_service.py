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

    def generate_event_pdf(self, event_id: str) -> Optional[bytes]:
        data = self.generate_event_report(event_id)
        if not data:
            return None
            
        try:
            from fpdf import FPDF
        except ImportError:
            return None
            
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Title
        pdf.set_font("Helvetica", style="B", size=16)
        pdf.cell(0, 10, txt="Agni-Netra Event Report", align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 10, txt=str(data.get('title', '')), align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(6)
        
        # Basic Info
        pdf.set_font("Helvetica", size=11)
        pdf.cell(0, 6, txt=f"Event ID: {data.get('event_id', '')}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, txt=f"Location: {data.get('location', '')}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, txt=f"Status: {data.get('verification_status', '')}", new_x="LMARGIN", new_y="NEXT")
        
        ai_data = data.get('ai_intelligence', {})
        pdf.cell(0, 6, txt=f"Priority: {ai_data.get('priority_level', '')}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(6)
        
        # Intelligence
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.cell(0, 8, txt="AI Intelligence Assessment", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=10)
        
        assessment = ai_data.get('current_assessment', '')
        if assessment:
            pdf.multi_cell(0, 6, txt=f"Assessment: {assessment}", new_x="LMARGIN", new_y="NEXT")
            
        hypothesis = ai_data.get('source_hypothesis', '')
        if hypothesis:
            pdf.multi_cell(0, 6, txt=f"Hypothesis: {hypothesis}", new_x="LMARGIN", new_y="NEXT")
            
        pdf.cell(0, 6, txt=f"Confidence: {ai_data.get('confidence', '')}%", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, txt=f"Risk Level: {ai_data.get('risk_level', '')} (Index: {ai_data.get('risk_index', '')})", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(6)
        
        # Evidence
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.cell(0, 8, txt="Evidence Sources", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=10)
        for ev in data.get('evidence', []):
            pdf.multi_cell(0, 6, txt=f"- {ev.get('source', '')} ({ev.get('direction', '')}): {ev.get('explanation', '')}", new_x="LMARGIN", new_y="NEXT")
            
        # Explanations
        pdf.ln(4)
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.cell(0, 8, txt="Explanations", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=10)
        explanations = data.get('explanations', {})
        why = explanations.get('why', '')
        if isinstance(why, list):
            why = "; ".join(str(w) for w in why)
        if why:
            pdf.multi_cell(0, 6, txt=f"Why: {why}", new_x="LMARGIN", new_y="NEXT")
            
        why_not = explanations.get('why_not', '')
        if isinstance(why_not, list):
            why_not = "; ".join(str(w) for w in why_not)
        if why_not:
            pdf.multi_cell(0, 6, txt=f"Why Not: {why_not}", new_x="LMARGIN", new_y="NEXT")
            
        return bytes(pdf.output())
