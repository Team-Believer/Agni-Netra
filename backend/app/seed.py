import sys
import argparse
from pathlib import Path
import datetime
import json

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.database.database import init_db, SessionLocal
from backend.app.database.models import (
    Event, Observation, EventObservation, EventEvidence, EventPrediction,
    RiskScore, PriorityScore, Alert, DataSource, AuditLog, VerificationRecord, Facility
)

def clear_seed_data(db):
    print("Clearing old seed data...")
    db.query(VerificationRecord).filter(VerificationRecord.data_mode == "SEED").delete()
    db.query(Alert).filter(Alert.data_mode == "SEED").delete()
    db.query(EventEvidence).filter(EventEvidence.data_mode == "SEED").delete()
    # RiskScore, PriorityScore, EventObservation are cascaded when Event is deleted
    db.query(Observation).filter(Observation.data_mode == "SEED").delete()
    db.query(Event).filter(Event.data_mode == "SEED").delete()
    db.query(Facility).filter(Facility.data_mode == "SEED").delete()
    db.commit()
    print("Seed data cleared.")

def seed_database():
    print("Initializing database...")
    init_db()
    db = SessionLocal()

    clear_seed_data(db)

    print("Seeding Data Sources...")
    # Add dummy sources if they don't exist
    if db.query(DataSource).count() == 0:
        data_sources = [
            {"name": "NASA FIRMS (VIIRS 375m)", "source_type": "SATELLITE_LEO", "status": "ONLINE", "coverage": "India Regional", "record_count": 1420, "latency_ms": 110},
            {"name": "INSAT-3DS Rapid Imager", "source_type": "SATELLITE_GEO", "status": "ONLINE", "coverage": "Indian Subcontinent (15m)", "record_count": 8640, "latency_ms": 45},
            {"name": "ESA Sentinel-2 MSI (SWIR)", "source_type": "SATELLITE_LEO", "status": "ONLINE", "coverage": "High-Res 20m Multi-spectral", "record_count": 210, "latency_ms": 320},
            {"name": "IMD Surface & Plume Wind", "source_type": "WEATHER", "status": "ONLINE", "coverage": "National AWS Network", "record_count": 3500, "latency_ms": 80},
            {"name": "OSM & GIDC Industrial GIS", "source_type": "ANCILLARY_GIS", "status": "ONLINE", "coverage": "Pan-India Critical Assets", "record_count": 480, "latency_ms": 25},
        ]
        for s in data_sources:
            db.add(DataSource(**s))
        db.commit()

    now = datetime.datetime.utcnow()

    # 1. FACILITIES (Chhattisgarh focus)
    facilities = [
        {
            "facility_id": "FAC-CG-001", "facility_name": "Bhilai Steel Plant", "category": "Metallurgical Works", 
            "state": "Chhattisgarh", "district": "Durg", "latitude": 21.19, "longitude": 81.38, 
            "industrial_area": "Bhilai", "description": "Major steel production facility.",
            "contact_name": "Control Room A", "contact_role": "Plant Manager", "contact_number": "+91-0000000001",
            "contact_source": "Seed Contact", "data_mode": "SEED"
        },
        {
            "facility_id": "FAC-CG-002", "facility_name": "Korba Super Thermal Power", "category": "Power Plant", 
            "state": "Chhattisgarh", "district": "Korba", "latitude": 22.39, "longitude": 82.68, 
            "industrial_area": "Korba", "description": "Coal-fired power station.",
            "contact_name": "Safety Desk", "contact_role": "Safety Officer", "contact_number": "+91-0000000002",
            "contact_source": "Seed Contact", "data_mode": "SEED"
        },
        {
            "facility_id": "FAC-CG-003", "facility_name": "Raipur Industrial Area", "category": "Industrial Park", 
            "state": "Chhattisgarh", "district": "Raipur", "latitude": 21.25, "longitude": 81.63, 
            "industrial_area": "Raipur", "description": "Mixed industrial manufacturing.",
            "contact_name": "Zone Manager", "contact_role": "GIDC Supervisor", "contact_number": "+91-0000000003",
            "contact_source": "Seed Contact", "data_mode": "SEED"
        },
        {
            "facility_id": "FAC-GJ-001", "facility_name": "Reliance Refinery", "category": "Petroleum Refinery", 
            "state": "Gujarat", "district": "Jamnagar", "latitude": 22.34, "longitude": 69.87, 
            "industrial_area": "Jamnagar", "description": "World's largest oil refinery complex.",
            "contact_name": "Security Desk", "contact_role": "Safety Lead", "contact_number": "+91-0000000004",
            "contact_source": "Seed Contact", "data_mode": "SEED"
        },
    ]
    for f in facilities:
        db.add(Facility(**f))
    db.commit()

    # 2. SCENARIO A: Routine Flare (Bhilai)
    ev_a = Event(
        event_id="EVENT-SEED-001", title="Routine Flare", location_name="Bhilai, Chhattisgarh", district="Durg", state="Chhattisgarh",
        nearby_facility="Bhilai Steel Plant", facility_type="Metallurgical Works", first_detected=now - datetime.timedelta(hours=6),
        last_observed=now - datetime.timedelta(hours=1), centroid_lat=21.19, centroid_lon=81.38,
        observation_count=6, current_state="Persistent", source_hypothesis="Routine Flare", behavior="Stable",
        abnormality="Normal", risk_level="Low", risk_index=15.0, priority_level="Low", confidence=0.96,
        evidence_completeness=0.88, verification_status="Monitoring", frp_change_pct=-4.0, footprint_expansion_factor=1.0,
        current_assessment="Normal continuous flaring at facility.",
        satellite_image_url="/demo-flare.png",
        why_explanation=["Matches known flare location.", "Stable FRP."],
        why_not_explanation=["No spatial expansion."],
        what_changed_explanation=["No significant changes."],
        data_mode="SEED"
    )
    db.add(ev_a)
    
    # SCENARIO B: Potential Industrial Fire (Korba)
    ev_b = Event(
        event_id="EVENT-SEED-002", title="Industrial Fire (Hypothesis)", location_name="Korba, Chhattisgarh", district="Korba", state="Chhattisgarh",
        nearby_facility="Korba Super Thermal Power", facility_type="Power Plant", first_detected=now - datetime.timedelta(hours=4),
        last_observed=now, centroid_lat=22.39, centroid_lon=82.68,
        observation_count=4, current_state="Active", source_hypothesis="Industrial Fire", behavior="Escalating",
        abnormality="Highly Abnormal", risk_level="Critical", risk_index=88.0, priority_level="High", confidence=0.89,
        evidence_completeness=0.74, verification_status="Needs Verification", frp_change_pct=140.0, footprint_expansion_factor=2.1,
        current_assessment="Severe heat burst adjacent to plant structures.",
        satellite_image_url="/demo-fire.png",
        why_explanation=["Expanding thermal footprint.", "FRP surge +140%."],
        why_not_explanation=["Not a Routine Flare: Expanding beyond stack bounds."],
        what_changed_explanation=["FRP surged rapidly in last 4 hours."],
        data_mode="SEED"
    )
    db.add(ev_b)

    # SCENARIO C: Forest Fire
    ev_c = Event(
        event_id="EVENT-SEED-003", title="Forest Fire", location_name="Barnawapara Reserve, Chhattisgarh", district="Raipur", state="Chhattisgarh",
        nearby_facility="Forest Reserve", facility_type="Forest", first_detected=now - datetime.timedelta(days=1),
        last_observed=now - datetime.timedelta(minutes=30), centroid_lat=21.39, centroid_lon=82.38,
        observation_count=8, current_state="Active", source_hypothesis="Forest Fire", behavior="Expanding",
        abnormality="Normal", risk_level="Medium", risk_index=55.0, priority_level="Medium", confidence=0.92,
        evidence_completeness=0.80, verification_status="Needs Verification", frp_change_pct=40.0, footprint_expansion_factor=1.5,
        current_assessment="Vegetation fire spreading north.",
        satellite_image_url="/demo-placeholder.jpg",
        data_mode="SEED"
    )
    db.add(ev_c)
    
    # SCENARIO D: Agricultural Fire
    ev_d = Event(
        event_id="EVENT-SEED-004", title="Agricultural Burn", location_name="Bemetara, Chhattisgarh", district="Bemetara", state="Chhattisgarh",
        nearby_facility="Farmland", facility_type="Agriculture", first_detected=now - datetime.timedelta(hours=12),
        last_observed=now - datetime.timedelta(hours=10), centroid_lat=21.69, centroid_lon=81.54,
        observation_count=2, current_state="Resolved", source_hypothesis="Agricultural Fire", behavior="Transient",
        abnormality="Normal", risk_level="Low", risk_index=10.0, priority_level="Monitor", confidence=0.85,
        evidence_completeness=0.60, verification_status="Monitoring", frp_change_pct=0.0, footprint_expansion_factor=1.0,
        current_assessment="Short duration post-harvest burning.",
        satellite_image_url="/demo-placeholder.jpg",
        data_mode="SEED"
    )
    db.add(ev_d)
    
    # SCENARIO E: Jamnagar Massive Industrial Fire
    ev_e = Event(
        event_id="EVENT-SEED-005", title="Refinery Critical Fire", location_name="Jamnagar, Gujarat", district="Jamnagar", state="Gujarat",
        nearby_facility="Reliance Refinery", facility_type="Petroleum Refinery", first_detected=now - datetime.timedelta(hours=2),
        last_observed=now, centroid_lat=22.34, centroid_lon=69.87,
        observation_count=12, current_state="Escalating", source_hypothesis="Industrial Fire", behavior="Sudden Spike",
        abnormality="Highly Abnormal", risk_level="Critical", risk_index=95.0, priority_level="Critical", confidence=0.98,
        evidence_completeness=0.95, verification_status="Needs Verification", frp_change_pct=450.0, footprint_expansion_factor=4.2,
        current_assessment="Massive uncontrolled heat burst and smoke plume at refinery tank farm.",
        satellite_image_url="/demo-jamnagar-fire.jpg",
        why_explanation=["Unprecedented FRP surge (+450%).", "Thick black smoke detected in optical sensors."],
        why_not_explanation=["Not a routine flare due to size and multisensor anomaly."],
        what_changed_explanation=["Multiple tank failures observed in last hour."],
        data_mode="SEED"
    )
    db.add(ev_e)

    # SCENARIO F: Unknown Anomaly
    ev_f = Event(
        event_id="EVENT-SEED-006", title="Unknown Thermal Anomaly", location_name="Bokaro, Jharkhand", district="Bokaro", state="Jharkhand",
        nearby_facility="Bokaro Steel Plant", facility_type="Metallurgical Works", first_detected=now - datetime.timedelta(hours=1),
        last_observed=now, centroid_lat=23.66, centroid_lon=86.15,
        observation_count=3, current_state="Active", source_hypothesis="Unknown", behavior="Unstable",
        abnormality="Highly Abnormal", risk_level="High", risk_index=72.0, priority_level="High", confidence=0.45,
        evidence_completeness=0.50, verification_status="Needs Verification", frp_change_pct=110.0, footprint_expansion_factor=1.2,
        current_assessment="Unidentified heat source near industrial boundary. Low confidence due to cloud cover.",
        satellite_image_url="/demo-placeholder.jpg",
        why_explanation=["Anomalous heat detection outside normal operational zones."],
        why_not_explanation=["Insufficient multi-sensor data to confirm industrial fire."],
        what_changed_explanation=["New detection in last hour."],
        data_mode="SEED"
    )
    db.add(ev_f)

    # SCENARIO G: Transient Agricultural Fire
    ev_g = Event(
        event_id="EVENT-SEED-007", title="Stubble Burning", location_name="Ludhiana, Punjab", district="Ludhiana", state="Punjab",
        nearby_facility="Agricultural Fields", facility_type="Agriculture", first_detected=now - datetime.timedelta(days=2),
        last_observed=now - datetime.timedelta(days=1, hours=20), centroid_lat=30.90, centroid_lon=75.85,
        observation_count=2, current_state="Resolved", source_hypothesis="Agricultural Fire", behavior="Transient",
        abnormality="Normal", risk_level="Low", risk_index=5.0, priority_level="Monitor", confidence=0.91,
        evidence_completeness=0.85, verification_status="Verified Active", frp_change_pct=0.0, footprint_expansion_factor=1.0,
        current_assessment="Post-harvest stubble burning verified and concluded.",
        satellite_image_url="/demo-placeholder.jpg",
        data_mode="SEED"
    )
    db.add(ev_g)

    # SCENARIO H: Routine Flare (Digboi)
    ev_h = Event(
        event_id="EVENT-SEED-008", title="Routine Flare", location_name="Digboi, Assam", district="Tinsukia", state="Assam",
        nearby_facility="Digboi Refinery", facility_type="Petroleum Refinery", first_detected=now - datetime.timedelta(days=5),
        last_observed=now, centroid_lat=27.38, centroid_lon=95.63,
        observation_count=45, current_state="Persistent", source_hypothesis="Routine Flare", behavior="Stable",
        abnormality="Normal", risk_level="Low", risk_index=12.0, priority_level="Low", confidence=0.97,
        evidence_completeness=0.90, verification_status="Monitoring", frp_change_pct=-2.0, footprint_expansion_factor=1.0,
        current_assessment="Historic continuous flare, operating within normal parameters.",
        satellite_image_url="/demo-placeholder.jpg",
        data_mode="SEED"
    )
    db.add(ev_h)

    # SCENARIO I: Forest Fire (Simlipal)
    ev_i = Event(
        event_id="EVENT-SEED-009", title="Major Forest Fire", location_name="Simlipal National Park, Odisha", district="Mayurbhanj", state="Odisha",
        nearby_facility="National Park", facility_type="Forest", first_detected=now - datetime.timedelta(days=3),
        last_observed=now - datetime.timedelta(minutes=15), centroid_lat=21.93, centroid_lon=86.37,
        observation_count=32, current_state="Active", source_hypothesis="Forest Fire", behavior="Expanding Rapidly",
        abnormality="Highly Abnormal", risk_level="High", risk_index=85.0, priority_level="High", confidence=0.94,
        evidence_completeness=0.88, verification_status="Needs Verification", frp_change_pct=210.0, footprint_expansion_factor=5.5,
        current_assessment="Large scale forest fire spreading across multiple sectors of the reserve.",
        satellite_image_url="/demo-placeholder.jpg",
        data_mode="SEED"
    )
    db.add(ev_i)

    # SCENARIO J: Industrial Anomaly (Paradip)
    ev_j = Event(
        event_id="EVENT-SEED-010", title="Industrial Smoldering", location_name="Paradip, Odisha", district="Jagatsinghpur", state="Odisha",
        nearby_facility="Paradip Port Industries", facility_type="Industrial Port", first_detected=now - datetime.timedelta(hours=8),
        last_observed=now - datetime.timedelta(hours=1), centroid_lat=20.26, centroid_lon=86.67,
        observation_count=6, current_state="Persistent", source_hypothesis="Industrial Fire", behavior="Smoldering",
        abnormality="Abnormal", risk_level="Medium", risk_index=60.0, priority_level="Medium", confidence=0.82,
        evidence_completeness=0.75, verification_status="Under Verification", frp_change_pct=15.0, footprint_expansion_factor=1.1,
        current_assessment="Low intensity but persistent heat anomaly at port storage area.",
        satellite_image_url="/demo-placeholder.jpg",
        data_mode="SEED"
    )
    db.add(ev_j)

    # SCENARIO K: Coal Mine Fire (Jharia)
    ev_k = Event(
        event_id="EVENT-SEED-011", title="Underground Coal Fire", location_name="Jharia, Jharkhand", district="Dhanbad", state="Jharkhand",
        nearby_facility="Jharia Coalfield", facility_type="Mining", first_detected=now - datetime.timedelta(days=90),
        last_observed=now, centroid_lat=23.74, centroid_lon=86.41,
        observation_count=120, current_state="Persistent", source_hypothesis="Coal Mine Fire", behavior="Stable",
        abnormality="Normal", risk_level="Medium", risk_index=45.0, priority_level="Low", confidence=0.99,
        evidence_completeness=0.92, verification_status="Monitoring", frp_change_pct=1.0, footprint_expansion_factor=1.0,
        current_assessment="Known long-term underground coal seam fire. No sudden changes.",
        satellite_image_url="/demo-placeholder.jpg",
        data_mode="SEED"
    )
    db.add(ev_k)

    # SCENARIO L: Waste Burning (Delhi)
    ev_l = Event(
        event_id="EVENT-SEED-012", title="Landfill Fire", location_name="Ghazipur, Delhi", district="East Delhi", state="Delhi",
        nearby_facility="Ghazipur Landfill", facility_type="Waste Management", first_detected=now - datetime.timedelta(hours=48),
        last_observed=now - datetime.timedelta(hours=2), centroid_lat=28.62, centroid_lon=77.32,
        observation_count=15, current_state="Active", source_hypothesis="Landfill Fire", behavior="Smoldering",
        abnormality="Abnormal", risk_level="Medium", risk_index=65.0, priority_level="Medium", confidence=0.88,
        evidence_completeness=0.78, verification_status="Needs Verification", frp_change_pct=50.0, footprint_expansion_factor=1.4,
        current_assessment="Significant surface burning at landfill site.",
        satellite_image_url="/demo-placeholder.jpg",
        data_mode="SEED"
    )
    db.add(ev_l)

    db.commit()

    # Create Evidence Time-series (Analytics Deterministic Data) for EVENT-SEED-002
    evs_timeline = [
        {"timestamp": now - datetime.timedelta(hours=4), "quality": 0.25, "source": "VIIRS"},
        {"timestamp": now - datetime.timedelta(hours=3, minutes=30), "quality": 0.42, "source": "INSAT-3D"},
        {"timestamp": now - datetime.timedelta(hours=3), "quality": 0.71, "source": "VIIRS"},
        {"timestamp": now - datetime.timedelta(hours=2, minutes=30), "quality": 0.48, "source": "INSAT-3D"},
        {"timestamp": now - datetime.timedelta(hours=2), "quality": 0.82, "source": "SENTINEL-2"},
        {"timestamp": now - datetime.timedelta(hours=1, minutes=30), "quality": 0.61, "source": "IMD_WEATHER"},
        {"timestamp": now - datetime.timedelta(hours=1), "quality": 0.90, "source": "VIIRS"},
    ]
    for ts in evs_timeline:
        db.add(EventEvidence(
            event_id="EVENT-SEED-002", source=ts["source"], sensor="Multi", evidence_type="Contextual",
            timestamp=ts["timestamp"], quality=ts["quality"], relevance=1.0, direction="SUPPORTING",
            explanation=f"Corroboration via {ts['source']}.", data_mode="SEED"
        ))
    db.commit()

    # Add Observation
    obs = Observation(
        source="NASA_FIRMS_VIIRS", source_observation_id="OBS-SEED-001",
        latitude=22.39, longitude=82.68, timestamp=now,
        frp=150.0, brightness_temperature=340.0, confidence=0.89, satellite_sensor="VIIRS_SNPP",
        spatial_resolution=375.0, observation_quality="NOMINAL", data_mode="SEED"
    )
    db.add(obs)
    db.commit()
    db.add(EventObservation(event_id="EVENT-SEED-002", observation_id=obs.id, sequence_number=1))
    db.commit()

    print("Seed data successfully injected (Chhattisgarh focus).")
    db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Clear old seed data before seeding")
    args = parser.parse_args()

    print("==========================================================")
    print("  Agni-Netra: Seeding Realistic Spaceborne Demo Data")
    print("==========================================================")
    
    seed_database()
