import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Agni-Netra" in data["service"]

def test_dashboard_summary():
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_active" in data
    assert "high_priority" in data
    assert "under_verification" in data
    assert "resolved_24h" in data
    assert data["total_active"] >= 10

def test_events_list_and_detail():
    response = client.get("/api/events")
    assert response.status_code == 200
    events = response.json()
    assert len(events) > 0

    # Test EVENT-SEED-005 details (Jamnagar Refinery)
    res_05 = client.get("/api/events/EVENT-SEED-005")
    assert res_05.status_code == 200
    data_05 = res_05.json()
    assert data_05["event_id"] == "EVENT-SEED-005"
    assert "Jamnagar" in data_05["nearby_facility"] or "Reliance" in data_05["nearby_facility"]
    assert len(data_05["evidence"]) > 0
    assert len(data_05["explanations"]["why"]) > 0

def test_verification_workflow():
    payload = {
        "decision": "confirmed",
        "comment": "Confirmed by analyst following high-resolution thermal corroboration.",
        "reviewer": "Lead Analyst"
    }
    response = client.post("/api/events/EVENT-SEED-005/verify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["new_status"] == "Confirmed"

    # Reset back to Needs Verification for demo stability
    reset_payload = {
        "decision": "needs_more_evidence",
        "comment": "Resetting for demonstration state.",
        "reviewer": "System"
    }
    client.post("/api/events/EVENT-SEED-005/verify", json=reset_payload)

def test_sources_status():
    response = client.get("/api/sources/status")
    assert response.status_code == 200
    data = response.json()
    assert data["online_sources"] >= 5

def test_reports_and_models():
    # Report
    rep_res = client.get("/api/reports/EVENT-SEED-005")
    assert rep_res.status_code == 200
    rep_data = rep_res.json()
    assert rep_data.get("event_id") == "EVENT-SEED-005" or rep_data.get("event_identity", {}).get("event_id") == "EVENT-SEED-005"

    # Models
    mod_res = client.get("/api/models/status")
    assert mod_res.status_code == 200
    assert mod_res.json()["status"] == "READY"
