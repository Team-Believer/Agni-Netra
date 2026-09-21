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
    db.query(VerificationRecord).filter(VerificationRecord.data_mode == "SEED").delete(synchronize_session=False)
    db.query(Alert).filter(Alert.data_mode == "SEED").delete(synchronize_session=False)
    db.query(EventEvidence).filter(EventEvidence.data_mode == "SEED").delete(synchronize_session=False)
    db.query(EventPrediction).delete(synchronize_session=False)
    
    # Clear EventObservation relationships linked to seed events
    seed_event_ids = [e.event_id for e in db.query(Event.event_id).filter(Event.data_mode == "SEED").all()]
    if seed_event_ids:
        db.query(EventObservation).filter(EventObservation.event_id.in_(seed_event_ids)).delete(synchronize_session=False)
    
    db.query(Observation).filter(Observation.data_mode == "SEED").delete(synchronize_session=False)
    db.query(Event).filter(Event.data_mode == "SEED").delete(synchronize_session=False)
    db.query(Facility).filter(Facility.data_mode == "SEED").delete(synchronize_session=False)
    db.commit()
    print("Seed data cleared.")

def seed_database():
    print("Initializing database...")
    init_db()
    db = SessionLocal()

    clear_seed_data(db)

    print("Seeding Data Sources...")
    if db.query(DataSource).count() == 0:
        data_sources = [
            {"name": "NASA FIRMS (VIIRS 375m)", "source_type": "SATELLITE_LEO", "status": "ONLINE", "coverage": "India Regional", "record_count": 1420, "latency_ms": 110},
            {"name": "INSAT-3DS Rapid Imager", "source_type": "SATELLITE_GEO", "status": "ONLINE", "coverage": "Indian Subcontinent (15m)", "record_count": 8640, "latency_ms": 45},
            {"name": "ESA Sentinel-2 MSI (SWIR)", "source_type": "SATELLITE_LEO", "status": "ONLINE", "coverage": "High-Res 20m Multi-spectral", "record_count": 210, "latency_ms": 320},
            {"name": "IMD Surface & Plume Wind", "source_type": "WEATHER", "status": "ONLINE", "coverage": "National AWS Network", "record_count": 3500, "latency_ms": 80},
            {"name": "OSM & GIDC Industrial GIS", "source_type": "ANCILLARY_GIS", "status": "ONLINE", "coverage": "Pan-India Critical Assets", "record_count": 480, "latency_ms": 25},
            {"name": "ESA Sentinel-1 SAR", "source_type": "RADAR_SAR", "status": "ONLINE", "coverage": "All-weather structural radar", "record_count": 140, "latency_ms": 450},
            {"name": "TROPOMI Atmospheric Plume", "source_type": "ATMOSPHERIC", "status": "ONLINE", "coverage": "NO2 / CO trace gas", "record_count": 92, "latency_ms": 390},
        ]
        for s in data_sources:
            db.add(DataSource(**s))
        db.commit()

    now = datetime.datetime.utcnow()

    # 1. SEED FACILITIES
    facilities = [
        {
            "facility_id": "FAC-GJ-001", "facility_name": "Reliance Refinery", "category": "Petroleum Refinery",
            "state": "Gujarat", "district": "Jamnagar", "latitude": 22.34, "longitude": 69.87,
            "industrial_area": "Jamnagar GIDC Complex", "description": "World's largest petroleum refinery complex.",
            "contact_name": "Safety Desk", "contact_role": "Safety Lead", "contact_number": "+91-0000000001",
            "contact_source": "Seed Contact", "data_mode": "SEED"
        },
        {
            "facility_id": "FAC-CG-002", "facility_name": "Korba Super Thermal Power", "category": "Power Plant",
            "state": "Chhattisgarh", "district": "Korba", "latitude": 22.39, "longitude": 82.68,
            "industrial_area": "Korba Industrial Zone", "description": "Major coal-fired thermal power station.",
            "contact_name": "Control Room A", "contact_role": "Plant Supervisor", "contact_number": "+91-0000000002",
            "contact_source": "Seed Contact", "data_mode": "SEED"
        },
        {
            "facility_id": "FAC-JH-001", "facility_name": "Bokaro Steel Plant", "category": "Steel Plant",
            "state": "Jharkhand", "district": "Bokaro", "latitude": 23.66, "longitude": 86.15,
            "industrial_area": "Bokaro Steel City", "description": "Integrated steel manufacturing facility.",
            "contact_name": "Safety Desk", "contact_role": "Industrial Safety Officer", "contact_number": "+91-0000000003",
            "contact_source": "Seed Contact", "data_mode": "SEED"
        },
        {
            "facility_id": "FAC-AS-001", "facility_name": "Digboi Refinery", "category": "Petroleum Refinery",
            "state": "Assam", "district": "Tinsukia", "latitude": 27.38, "longitude": 95.63,
            "industrial_area": "Digboi Industrial Belt", "description": "Historic legacy petroleum refinery.",
            "contact_name": "Operations Lead", "contact_role": "Refinery Manager", "contact_number": "+91-0000000004",
            "contact_source": "Seed Contact", "data_mode": "SEED"
        },
        {
            "facility_id": "FAC-JH-002", "facility_name": "Jharia Coalfield", "category": "Mining",
            "state": "Jharkhand", "district": "Dhanbad", "latitude": 23.74, "longitude": 86.41,
            "industrial_area": "Jharia Mining Sector", "description": "Underground coal seam mining area.",
            "contact_name": "Mining Desk", "contact_role": "Field Inspector", "contact_number": "+91-0000000005",
            "contact_source": "Seed Contact", "data_mode": "SEED"
        },
        {
            "facility_id": "FAC-CG-001", "facility_name": "Bhilai Steel Plant", "category": "Steel Plant",
            "state": "Chhattisgarh", "district": "Durg", "latitude": 21.19, "longitude": 81.38,
            "industrial_area": "Bhilai GIDC", "description": "Integrated steel rail manufacturing complex.",
            "contact_name": "Plant Desk", "contact_role": "Duty Manager", "contact_number": "+91-0000000006",
            "contact_source": "Seed Contact", "data_mode": "SEED"
        },
        {
            "facility_id": "FAC-OD-001", "facility_name": "Paradip Port Industries", "category": "Industrial Port",
            "state": "Odisha", "district": "Jagatsinghpur", "latitude": 20.26, "longitude": 86.67,
            "industrial_area": "Paradip Chemical Zone", "description": "Deepwater port chemical terminal.",
            "contact_name": "Port Control", "contact_role": "Port Safety Officer", "contact_number": "+91-0000000007",
            "contact_source": "Seed Contact", "data_mode": "SEED"
        },
        {
            "facility_id": "FAC-OD-002", "facility_name": "Simlipal Reserve Boundary", "category": "Forest",
            "state": "Odisha", "district": "Mayurbhanj", "latitude": 21.93, "longitude": 86.37,
            "industrial_area": "Simlipal Sector", "description": "National park forest reserve boundary.",
            "contact_name": "Forest Range Desk", "contact_role": "Chief Ranger", "contact_number": "+91-0000000008",
            "contact_source": "Seed Contact", "data_mode": "SEED"
        },
        {
            "facility_id": "FAC-MH-001", "facility_name": "Nagpur Industrial Zone", "category": "Industrial Park",
            "state": "Maharashtra", "district": "Nagpur", "latitude": 21.14, "longitude": 79.08,
            "industrial_area": "MIDC Hingna", "description": "Manufacturing and chemical processing hub.",
            "contact_name": "MIDC Control", "contact_role": "Zone Supervisor", "contact_number": "+91-0000000009",
            "contact_source": "Seed Contact", "data_mode": "SEED"
        },
        {
            "facility_id": "FAC-HR-001", "facility_name": "Karnal Agricultural Belt", "category": "Agriculture",
            "state": "Haryana", "district": "Karnal", "latitude": 29.68, "longitude": 76.99,
            "industrial_area": "Karnal Rural Belt", "description": "Post-harvest paddy agricultural hub.",
            "contact_name": "Agri Extension Desk", "contact_role": "District Officer", "contact_number": "+91-0000000010",
            "contact_source": "Seed Contact", "data_mode": "SEED"
        },
        {
            "facility_id": "FAC-CG-003", "facility_name": "Barnawapara Reserve Boundary", "category": "Forest",
            "state": "Chhattisgarh", "district": "Raipur", "latitude": 21.39, "longitude": 82.38,
            "industrial_area": "Barnawapara Sector", "description": "State forest reserve boundary.",
            "contact_name": "Reserve Range Desk", "contact_role": "Forest Guard", "contact_number": "+91-0000000011",
            "contact_source": "Seed Contact", "data_mode": "SEED"
        },
        {
            "facility_id": "FAC-CG-004", "facility_name": "Bemetara Rural Belt", "category": "Agriculture",
            "state": "Chhattisgarh", "district": "Bemetara", "latitude": 21.69, "longitude": 81.54,
            "industrial_area": "Bemetara Sector", "description": "Agricultural farming belt.",
            "contact_name": "KVK Center", "contact_role": "Agri Officer", "contact_number": "+91-0000000012",
            "contact_source": "Seed Contact", "data_mode": "SEED"
        },
        {
            "facility_id": "FAC-PB-001", "facility_name": "Ludhiana Farm Belt", "category": "Agriculture",
            "state": "Punjab", "district": "Ludhiana", "latitude": 30.90, "longitude": 75.85,
            "industrial_area": "Ludhiana Rural Sector", "description": "Major crop residue burning zone.",
            "contact_name": "PAU Extension Desk", "contact_role": "Field Supervisor", "contact_number": "+91-0000000013",
            "contact_source": "Seed Contact", "data_mode": "SEED"
        },
        {
            "facility_id": "FAC-DL-001", "facility_name": "Ghazipur Landfill Facility", "category": "Waste Management",
            "state": "Delhi", "district": "East Delhi", "latitude": 28.62, "longitude": 77.32,
            "industrial_area": "Ghazipur Industrial Sector", "description": "Municipal solid waste processing site.",
            "contact_name": "MCD Control Room", "contact_role": "Site In-Charge", "contact_number": "+91-0000000014",
            "contact_source": "Seed Contact", "data_mode": "SEED"
        }
    ]
    for f in facilities:
        db.add(Facility(**f))
    db.commit()

    # 2. HERO DEMO EVENT: EVENT-SEED-005 (Jamnagar Refinery Critical Fire)
    e005_first = now - datetime.timedelta(hours=2)
    e005_last = now - datetime.timedelta(minutes=5)
    
    ev_005 = Event(
        event_id="EVENT-SEED-005",
        title="Refinery Critical Fire",
        location_name="Jamnagar, Gujarat",
        district="Jamnagar",
        state="Gujarat",
        nearby_facility="Reliance Refinery",
        facility_type="Petroleum Refinery",
        first_detected=e005_first,
        last_observed=e005_last,
        centroid_lat=22.34,
        centroid_lon=69.87,
        bounding_geojson=json.dumps({
            "type": "Polygon",
            "coordinates": [[[69.85, 22.32], [69.89, 22.32], [69.89, 22.36], [69.85, 22.36], [69.85, 22.32]]]
        }),
        observation_count=12,
        current_state="Escalating",
        source_hypothesis="Industrial Fire",
        behavior="Sudden Spike",
        abnormality="Highly Abnormal",
        risk_level="Critical",
        risk_index=95.0,
        priority_level="Critical",
        confidence=0.98,
        evidence_completeness=0.95,
        verification_status="Needs Verification",
        frp_change_pct=450.0, # Baseline 87.3 MW -> Current 480.0 MW: +450%
        footprint_expansion_factor=4.2,
        current_assessment="Massive uncontrolled heat burst and thick smoke plume at refinery tank farm sector.",
        satellite_image_url="/demo-jamnagar-fire.jpg",
        why_explanation=[
            "Unprecedented FRP surge (+450% above historical baseline average of 87.3 MW).",
            "Spatial thermal footprint expanded 4.2x across 12 consecutive satellite passes in 2 hours.",
            "High-resolution 20m Sentinel-2 SWIR B12 peak intensity corroboration.",
            "Structural anomaly detected by Sentinel-1 SAR at Storage Tank Farm 4."
        ],
        why_not_explanation=[
            "Not a Routine Flare: Spatial thermal radius expands far beyond registered flare stack bounds.",
            "Not Agricultural Burning: Centered squarely within crude distillation and catalytic cracking unit boundary.",
            "Not Sensor Glint: Multi-spectral corroboration across SNPP VIIRS, NOAA-20 VIIRS, and INSAT-3DS."
        ],
        what_changed_explanation=[
            "FRP surged from 42 MW to 480 MW over the last 120 minutes.",
            "Thermal footprint expanded 4.2x across 4 adjacent sub-pixel cells.",
            "12 multi-sensor overpass observations recorded in last 2 hours."
        ],
        data_mode="SEED"
    )
    db.add(ev_005)
    db.commit()

    # Seed 12 connected Observations for EVENT-SEED-005
    obs_005_data = [
        {"time_offset": 120, "frp": 42.0, "bt": 335.0, "sensor": "VIIRS_SNPP", "lat": 22.338, "lon": 69.868},
        {"time_offset": 110, "frp": 58.5, "bt": 342.0, "sensor": "INSAT_3DS", "lat": 22.339, "lon": 69.869},
        {"time_offset": 100, "frp": 76.0, "bt": 350.0, "sensor": "VIIRS_NOAA20", "lat": 22.339, "lon": 69.870},
        {"time_offset": 90,  "frp": 112.0, "bt": 362.0, "sensor": "INSAT_3DS", "lat": 22.340, "lon": 69.870},
        {"time_offset": 80,  "frp": 155.0, "bt": 375.0, "sensor": "SENTINEL_2", "lat": 22.341, "lon": 69.871},
        {"time_offset": 70,  "frp": 210.0, "bt": 388.0, "sensor": "VIIRS_SNPP", "lat": 22.341, "lon": 69.871},
        {"time_offset": 60,  "frp": 268.0, "bt": 398.0, "sensor": "INSAT_3DS", "lat": 22.342, "lon": 69.872},
        {"time_offset": 50,  "frp": 325.0, "bt": 405.0, "sensor": "VIIRS_NOAA20", "lat": 22.342, "lon": 69.872},
        {"time_offset": 40,  "frp": 380.0, "bt": 412.0, "sensor": "INSAT_3DS", "lat": 22.343, "lon": 69.873},
        {"time_offset": 30,  "frp": 420.0, "bt": 418.0, "sensor": "VIIRS_SNPP", "lat": 22.343, "lon": 69.873},
        {"time_offset": 15,  "frp": 455.0, "bt": 422.0, "sensor": "SENTINEL_2", "lat": 22.344, "lon": 69.874},
        {"time_offset": 5,   "frp": 480.0, "bt": 425.0, "sensor": "VIIRS_NOAA20", "lat": 22.344, "lon": 69.874},
    ]
    for idx, item in enumerate(obs_005_data, 1):
        ts = now - datetime.timedelta(minutes=item["time_offset"])
        obs = Observation(
            source="SATELLITE_MULTI",
            source_observation_id=f"OBS-SEED-005-{idx:02d}",
            latitude=item["lat"],
            longitude=item["lon"],
            timestamp=ts,
            frp=item["frp"],
            brightness_temperature=item["bt"],
            confidence=0.98,
            satellite_sensor=item["sensor"],
            spatial_resolution=375.0 if "VIIRS" in item["sensor"] else (20.0 if "SENTINEL" in item["sensor"] else 1000.0),
            observation_quality="NOMINAL",
            smoke_flag=True,
            saturation_flag=item["frp"] > 250.0,
            data_mode="SEED"
        )
        db.add(obs)
        db.commit()
        db.add(EventObservation(event_id="EVENT-SEED-005", observation_id=obs.id, sequence_number=idx))
    db.commit()

    # Seed 10 Evidence Ledger items for EVENT-SEED-005 (SAR AVAILABLE)
    evs_005_ledger = [
        {"source": "NASA_FIRMS_VIIRS", "evidence_type": "Thermal", "direction": "SUPPORTING", "quality": 0.98, "relevance": 1.0, "value": "Max FRP 480.0 MW (+450%)", "explanation": "Demo FIRMS VIIRS detections confirm acute escalation in radiative thermal output over 12 passes."},
        {"source": "INSAT_3DS", "evidence_type": "Temporal", "direction": "SUPPORTING", "quality": 0.92, "relevance": 0.95, "value": "Continuous 15-min thermal burst", "explanation": "Synthetic INSAT-3DS MIR channel detects persistent non-pulsing thermal release over 2 hours."},
        {"source": "SENTINEL_2", "evidence_type": "Optical", "direction": "SUPPORTING", "quality": 0.96, "relevance": 0.98, "value": "SWIR B12 Peak + Dark Plume", "explanation": "Simulated Sentinel-2 20m SWIR 2.2μm band shows 4 adjacent saturated pixels with dense plume."},
        {"source": "SENTINEL_1", "evidence_type": "SAR", "direction": "SUPPORTING", "quality": 0.90, "relevance": 0.92, "value": "Structural anomaly at Tank 4", "explanation": "Demo Sentinel-1 C-band SAR backscatter reduction indicating structural thermal damage."},
        {"source": "IMD_WEATHER", "evidence_type": "Weather", "direction": "SUPPORTING", "quality": 0.88, "relevance": 0.85, "value": "Wind 18 km/h @ 225° (SW)", "explanation": "Demo weather feed: Downwind plume trajectory directing emissions northeast away from city center."},
        {"source": "OSM_GIDC_GIS", "evidence_type": "Facility", "direction": "SUPPORTING", "quality": 0.99, "relevance": 1.0, "value": "Reliance Jamnagar Refinery (0.1 km)", "explanation": "Direct spatial coincidence with crude distillation and tank farm boundary."},
        {"source": "HISTORICAL_FINGERPRINT", "evidence_type": "Historical", "direction": "SUPPORTING", "quality": 0.95, "relevance": 0.96, "value": "+450% over 90-day baseline (87.3 MW)", "explanation": "Radiative energy output exceeds 99.9th percentile of facility operating baseline record."},
        {"source": "TROPOMI_ATMOSPHERIC", "evidence_type": "Atmospheric", "direction": "MISSING", "quality": 0.50, "relevance": 0.40, "value": "Unavailable (Cloud Obstructed)", "explanation": "Simulated TROPOMI NO2/CO trace gas orbit pass obscured by coastal cloud top (demo provenance)."},
        {"source": "LAND_COVER_GIS", "evidence_type": "Spatial", "direction": "SUPPORTING", "quality": 0.94, "relevance": 0.90, "value": "Industrial Heavy Built-Up", "explanation": "Land cover classified as high-density heavy industrial processing infrastructure."},
        {"source": "TEMPORAL_RECURRENCE", "evidence_type": "Temporal", "direction": "SUPPORTING", "quality": 0.91, "relevance": 0.93, "value": "Non-cyclical sudden thermal spike", "explanation": "Pattern deviates completely from regular scheduled operational maintenance flaring."}
    ]
    for ev in evs_005_ledger:
        db.add(EventEvidence(event_id="EVENT-SEED-005", timestamp=e005_last, data_mode="SEED", **ev))
    db.commit()

    # Seed Verification Audit Trail for EVENT-SEED-005
    db.add(VerificationRecord(
        event_id="EVENT-SEED-005",
        reviewer="Agni-Netra AI Engine",
        decision="AI Classified",
        comment="Initial auto-detection raised Critical risk based on +450% FRP surge and multi-pixel spatial expansion.",
        previous_status=None,
        new_status="Needs Verification",
        timestamp=now - datetime.timedelta(hours=2),
        data_mode="SEED"
    ))
    db.add(VerificationRecord(
        event_id="EVENT-SEED-005",
        reviewer="Ananya Sharma",
        decision="Needs More Evidence",
        comment="Analyst Audit: Flagged for high-priority tasking and optical SWIR corroboration pass.",
        previous_status="Needs Verification",
        new_status="Needs Verification",
        timestamp=now - datetime.timedelta(hours=1),
        data_mode="SEED"
    ))
    db.commit()

    # Seed Alert for EVENT-SEED-005
    db.add(Alert(
        event_id="EVENT-SEED-005",
        alert_type="Industrial Thermal Escalation",
        severity="Critical",
        title="Critical Anomaly: Jamnagar Refinery, Gujarat",
        message="EVENT-SEED-005 exhibits +450% FRP surge with expanding footprint near primary processing units.",
        status="Active",
        data_mode="SEED"
    ))
    db.commit()

    # 3. OTHER MVP EVENTS (EVENT-SEED-001 TO EVENT-SEED-014)
    all_other_events = [
        # EVENT-SEED-002: Verification Candidate (SAR AVAILABLE)
        {
            "event_id": "EVENT-SEED-002", "title": "Industrial Fire (Hypothesis)", "location_name": "Korba, Chhattisgarh",
            "district": "Korba", "state": "Chhattisgarh", "nearby_facility": "Korba Super Thermal Power", "facility_type": "Power Plant",
            "first_detected": now - datetime.timedelta(hours=4), "last_observed": now - datetime.timedelta(minutes=15),
            "centroid_lat": 22.39, "centroid_lon": 82.68, "observation_count": 6,
            "current_state": "Active", "source_hypothesis": "Industrial Fire", "behavior": "Escalating", "abnormality": "Highly Abnormal",
            "risk_level": "Critical", "risk_index": 88.0, "priority_level": "High", "confidence": 0.89, "evidence_completeness": 0.74,
            "verification_status": "Needs Verification", "frp_change_pct": 140.0, "footprint_expansion_factor": 2.1,
            "current_assessment": "Severe heat burst adjacent to plant coal handling structures. High priority verification candidate.",
            "satellite_image_url": "/ind_fire_korba.jpg",
            "why": ["Expanding thermal footprint across 2.1x area.", "FRP surge +140% above 65.0 MW power plant baseline."],
            "why_not": ["Not a Routine Flare: Expanding beyond stack bounds."],
            "what_changed": ["FRP surged rapidly in last 4 hours."],
            "obs": [
                {"offset": 240, "frp": 65.0, "bt": 338.0, "sensor": "VIIRS_SNPP"},
                {"offset": 190, "frp": 82.0, "bt": 345.0, "sensor": "INSAT_3DS"},
                {"offset": 140, "frp": 105.0, "bt": 354.0, "sensor": "VIIRS_NOAA20"},
                {"offset": 90,  "frp": 125.0, "bt": 362.0, "sensor": "INSAT_3DS"},
                {"offset": 45,  "frp": 142.0, "bt": 370.0, "sensor": "SENTINEL_2"},
                {"offset": 15,  "frp": 156.0, "bt": 376.0, "sensor": "VIIRS_SNPP"},
            ],
            "evidences": [
                {"source": "NASA_FIRMS_VIIRS", "type": "Thermal", "dir": "SUPPORTING", "qual": 0.90, "rel": 1.0, "val": "Max FRP 156.0 MW (+140%)", "exp": "Demo VIIRS detections confirm persistent escalation over coal yards."},
                {"source": "INSAT_3DS", "type": "Temporal", "dir": "SUPPORTING", "qual": 0.85, "rel": 0.90, "val": "4-hour persistent thermal signature", "exp": "Synthetic geostationary feed shows non-decaying thermal output."},
                {"source": "OSM_GIDC_GIS", "type": "Facility", "dir": "SUPPORTING", "qual": 0.98, "rel": 1.0, "val": "Korba Power Station (0.2 km)", "exp": "Coincident with coal conveyer and stockpile area."},
                {"source": "SENTINEL_1", "type": "SAR", "dir": "SUPPORTING", "qual": 0.80, "rel": 0.85, "val": "Sub-surface hot spot anomaly", "exp": "Synthetic Sentinel-1 SAR context: Radar backscatter consistent with stockpile heating."},
                {"source": "IMD_WEATHER", "type": "Weather", "dir": "SUPPORTING", "qual": 0.82, "rel": 0.80, "val": "Wind 12 km/h E", "exp": "Plume blowing westward across plant boundary."},
                {"source": "HISTORICAL_FINGERPRINT", "type": "Historical", "dir": "SUPPORTING", "qual": 0.88, "rel": 0.92, "val": "+140% over 65 MW baseline", "exp": "Radiative output exceeds 98.5th percentile of historical plant baseline."}
            ]
        },

        # EVENT-SEED-006: Unknown / OOD Anomaly (SAR AVAILABLE)
        {
            "event_id": "EVENT-SEED-006", "title": "Unknown Thermal Anomaly", "location_name": "Bokaro, Jharkhand",
            "district": "Bokaro", "state": "Jharkhand", "nearby_facility": "Bokaro Steel Plant", "facility_type": "Steel Plant",
            "first_detected": now - datetime.timedelta(hours=3), "last_observed": now - datetime.timedelta(minutes=30),
            "centroid_lat": 23.66, "centroid_lon": 86.15, "observation_count": 3,
            "current_state": "Active", "source_hypothesis": "Unknown", "behavior": "Unstable", "abnormality": "Highly Abnormal",
            "risk_level": "High", "risk_index": 72.0, "priority_level": "High", "confidence": 0.45, "evidence_completeness": 0.42,
            "verification_status": "Needs Verification", "frp_change_pct": 110.0, "footprint_expansion_factor": 1.2,
            "current_assessment": "Unidentified heat source near industrial boundary. Low confidence due to cloud obstruction and conflicting sensor overpasses.",
            "satellite_image_url": "/ind_anomaly.jpg",
            "why": ["Anomalous heat detection outside registered furnace zones.", "FRP elevated +110% above baseline."],
            "why_not": ["Insufficient multi-sensor optical data to confirm industrial fire.", "Low confidence (45%) due to cloud tops."],
            "what_changed": ["Heavy cloud cover obstructing follow-up Sentinel passes."],
            "obs": [
                {"offset": 180, "frp": 45.0, "bt": 328.0, "sensor": "VIIRS_SNPP", "cloud": True},
                {"offset": 110, "frp": 62.0, "bt": 334.0, "sensor": "INSAT_3DS", "cloud": False},
                {"offset": 30,  "frp": 58.0, "bt": 331.0, "sensor": "VIIRS_NOAA20", "cloud": True},
            ],
            "evidences": [
                {"source": "NASA_FIRMS_VIIRS", "type": "Thermal", "dir": "SUPPORTING", "qual": 0.65, "rel": 0.80, "val": "FRP 62.0 MW (Cloud Obstructed)", "exp": "Demo VIIRS detection with high cloud flag present."},
                {"source": "SENTINEL_2", "type": "Optical", "dir": "MISSING", "qual": 0.30, "rel": 0.40, "val": "85% Cloud Coverage", "exp": "Simulated optical pass obscured by dense cloud top."},
                {"source": "SENTINEL_1", "type": "SAR", "dir": "SUPPORTING", "qual": 0.75, "rel": 0.80, "val": "Perimeter Structure Intact", "exp": "Synthetic Sentinel-1 SAR context: C-band radar backscatter indicates no structural damage to plant perimeter wall."},
                {"source": "INSAT_3DS", "type": "Temporal", "dir": "CONFLICTING", "qual": 0.55, "rel": 0.60, "val": "Intermittent Signal", "exp": "Synthetic geostationary signal fluctuating due to cloud top reflection."},
                {"source": "OSM_GIDC_GIS", "type": "Facility", "dir": "NEUTRAL", "qual": 0.85, "rel": 0.70, "val": "Bokaro Boundary (0.4 km)", "exp": "Located near plant perimeter boundary wall."}
            ]
        },

        # EVENT-SEED-008: Persistent Routine Flare (SAR UNAVAILABLE)
        {
            "event_id": "EVENT-SEED-008", "title": "Routine Flare", "location_name": "Digboi, Assam",
            "district": "Tinsukia", "state": "Assam", "nearby_facility": "Digboi Refinery", "facility_type": "Petroleum Refinery",
            "first_detected": now - datetime.timedelta(days=5), "last_observed": now - datetime.timedelta(minutes=20),
            "centroid_lat": 27.38, "centroid_lon": 95.63, "observation_count": 8,
            "current_state": "Persistent", "source_hypothesis": "Routine Flare", "behavior": "Stable", "abnormality": "Normal",
            "risk_level": "Low", "risk_index": 12.0, "priority_level": "Low", "confidence": 0.97, "evidence_completeness": 0.90,
            "verification_status": "Monitoring", "frp_change_pct": -2.0, "footprint_expansion_factor": 1.0,
            "current_assessment": "Historic continuous flare operating strictly within 90-day baseline parameters.",
            "satellite_image_url": "/routine_flare.jpg",
            "why": ["Fixed point source coordinates matching registered refinery flare stack.", "FRP matches historical baseline (24.0 MW)."],
            "why_not": ["No spatial expansion beyond stack radius.", "No abnormal thermal surge."],
            "what_changed": ["No significant variation across 5 days."],
            "obs": [
                {"offset": 2880, "frp": 24.5, "bt": 322.0, "sensor": "VIIRS_SNPP"},
                {"offset": 2160, "frp": 23.8, "bt": 321.0, "sensor": "VIIRS_NOAA20"},
                {"offset": 1440, "frp": 25.1, "bt": 323.0, "sensor": "INSAT_3DS"},
                {"offset": 720,  "frp": 24.0, "bt": 322.0, "sensor": "SENTINEL_2"},
                {"offset": 360,  "frp": 23.5, "bt": 321.0, "sensor": "VIIRS_SNPP"},
                {"offset": 180,  "frp": 24.2, "bt": 322.0, "sensor": "INSAT_3DS"},
                {"offset": 60,   "frp": 23.9, "bt": 321.5, "sensor": "VIIRS_NOAA20"},
                {"offset": 20,   "frp": 24.1, "bt": 322.0, "sensor": "INSAT_3DS"},
            ],
            "evidences": [
                {"source": "NASA_FIRMS_VIIRS", "type": "Thermal", "dir": "SUPPORTING", "qual": 0.95, "rel": 1.0, "val": "Stable FRP ~24 MW", "exp": "Demo VIIRS overpasses show zero thermal growth."},
                {"source": "OSM_GIDC_GIS", "type": "Facility", "dir": "SUPPORTING", "qual": 0.99, "rel": 1.0, "val": "Digboi Stack #2 (0.0 km)", "exp": "Direct 1:1 match with registered refinery flare stack coordinates."},
                {"source": "HISTORICAL_FINGERPRINT", "type": "Historical", "dir": "SUPPORTING", "qual": 0.98, "rel": 1.0, "val": "-2% vs 90-day baseline", "exp": "Thermal energy output strictly within historical flare operating window."}
            ]
        },

        # EVENT-SEED-011: Persistent Coal Seam Fire (SAR AVAILABLE)
        {
            "event_id": "EVENT-SEED-011", "title": "Underground Coal Fire", "location_name": "Jharia, Jharkhand",
            "district": "Dhanbad", "state": "Jharkhand", "nearby_facility": "Jharia Coalfield", "facility_type": "Mining",
            "first_detected": now - datetime.timedelta(days=90), "last_observed": now - datetime.timedelta(minutes=45),
            "centroid_lat": 23.74, "centroid_lon": 86.41, "observation_count": 10,
            "current_state": "Persistent", "source_hypothesis": "Coal Mine Fire", "behavior": "Stable", "abnormality": "Normal",
            "risk_level": "Medium", "risk_index": 45.0, "priority_level": "Low", "confidence": 0.99, "evidence_completeness": 0.92,
            "verification_status": "Monitoring", "frp_change_pct": 1.0, "footprint_expansion_factor": 1.0,
            "current_assessment": "Known long-term underground coal seam fire. No sudden thermal changes.",
            "satellite_image_url": "/coal_fire.jpg",
            "why": ["Continuous multi-month subsurface thermal signature.", "Located squarely in active Jharia open-cast coal seam."],
            "why_not": ["Not an industrial refinery fire.", "Not an agricultural burn."],
            "what_changed": ["Stable long-term smoldering behavior."],
            "obs": [
                {"offset": 10080, "frp": 39.5, "bt": 326.0, "sensor": "VIIRS_SNPP"},
                {"offset": 7200,  "frp": 40.1, "bt": 327.0, "sensor": "VIIRS_NOAA20"},
                {"offset": 4320,  "frp": 39.8, "bt": 326.5, "sensor": "INSAT_3DS"},
                {"offset": 2880,  "frp": 40.5, "bt": 327.2, "sensor": "SENTINEL_2"},
                {"offset": 1440,  "frp": 40.0, "bt": 326.8, "sensor": "VIIRS_SNPP"},
                {"offset": 720,   "frp": 39.7, "bt": 326.3, "sensor": "INSAT_3DS"},
                {"offset": 360,   "frp": 40.2, "bt": 327.0, "sensor": "VIIRS_NOAA20"},
                {"offset": 180,   "frp": 40.0, "bt": 326.8, "sensor": "INSAT_3DS"},
                {"offset": 90,    "frp": 39.9, "bt": 326.6, "sensor": "SENTINEL_2"},
                {"offset": 45,    "frp": 40.1, "bt": 326.9, "sensor": "VIIRS_SNPP"},
            ],
            "evidences": [
                {"source": "NASA_FIRMS_VIIRS", "type": "Thermal", "dir": "SUPPORTING", "qual": 0.96, "rel": 1.0, "val": "Steady FRP ~40 MW", "exp": "Demo VIIRS detections confirm multi-month underground heat signature."},
                {"source": "SENTINEL_1", "type": "SAR", "dir": "SUPPORTING", "qual": 0.85, "rel": 0.88, "val": "Ground Subsidence & Seam Cracking", "exp": "Synthetic Sentinel-1 SAR context: InSAR deformation mapping detects surface ground subsidence over smoldering seam."},
                {"source": "OSM_GIDC_GIS", "type": "Facility", "dir": "SUPPORTING", "qual": 0.99, "rel": 1.0, "val": "Jharia Coal Seam Sector 3", "exp": "Direct coincidence with registered active coal mining seam."},
                {"source": "HISTORICAL_FINGERPRINT", "type": "Historical", "dir": "SUPPORTING", "qual": 0.97, "rel": 1.0, "val": "+1% vs long-term baseline", "exp": "Smoldering thermal output matches multi-year underground coal fire fingerprint."}
            ]
        },

        # EVENT-SEED-001: Routine Flare (SAR UNAVAILABLE)
        {
            "event_id": "EVENT-SEED-001", "title": "Routine Flare", "location_name": "Bhilai, Chhattisgarh",
            "district": "Durg", "state": "Chhattisgarh", "nearby_facility": "Bhilai Steel Plant", "facility_type": "Steel Plant",
            "first_detected": now - datetime.timedelta(hours=6), "last_observed": now - datetime.timedelta(hours=1),
            "centroid_lat": 21.19, "centroid_lon": 81.38, "observation_count": 6,
            "current_state": "Persistent", "source_hypothesis": "Routine Flare", "behavior": "Stable", "abnormality": "Normal",
            "risk_level": "Low", "risk_index": 15.0, "priority_level": "Low", "confidence": 0.96, "evidence_completeness": 0.88,
            "verification_status": "Monitoring", "frp_change_pct": -4.0, "footprint_expansion_factor": 1.0,
            "current_assessment": "Normal continuous flaring at steel works.", "satellite_image_url": "/agri_fire_1.jpg",
            "why": ["Coincident with steel plant gas flare."], "why_not": ["No spatial expansion."], "what_changed": ["No significant variation."],
            "obs": [
                {"offset": 360, "frp": 18.0, "bt": 320.0, "sensor": "VIIRS_SNPP"},
                {"offset": 240, "frp": 17.5, "bt": 319.5, "sensor": "INSAT_3DS"},
                {"offset": 180, "frp": 18.2, "bt": 320.2, "sensor": "VIIRS_NOAA20"},
                {"offset": 120, "frp": 17.8, "bt": 319.8, "sensor": "INSAT_3DS"},
                {"offset": 90,  "frp": 17.6, "bt": 319.6, "sensor": "SENTINEL_2"},
                {"offset": 60,  "frp": 17.4, "bt": 319.4, "sensor": "VIIRS_SNPP"},
            ],
            "evidences": [
                {"source": "NASA_FIRMS_VIIRS", "type": "Thermal", "dir": "SUPPORTING", "qual": 0.92, "rel": 0.90, "val": "FRP 17.4 MW", "exp": "Demo VIIRS overpasses confirm nominal steel flare emissions."}
            ]
        },

        # EVENT-SEED-003: Forest Fire (SAR UNAVAILABLE)
        {
            "event_id": "EVENT-SEED-003", "title": "Forest Fire", "location_name": "Barnawapara Reserve, Chhattisgarh",
            "district": "Raipur", "state": "Chhattisgarh", "nearby_facility": "Barnawapara Reserve Boundary", "facility_type": "Forest",
            "first_detected": now - datetime.timedelta(days=1), "last_observed": now - datetime.timedelta(minutes=30),
            "centroid_lat": 21.39, "centroid_lon": 82.38, "observation_count": 5,
            "current_state": "Active", "source_hypothesis": "Forest Fire", "behavior": "Expanding", "abnormality": "Normal",
            "risk_level": "Medium", "risk_index": 55.0, "priority_level": "Medium", "confidence": 0.92, "evidence_completeness": 0.80,
            "verification_status": "Needs Verification", "frp_change_pct": 40.0, "footprint_expansion_factor": 1.5,
            "current_assessment": "Vegetation fire spreading along forest reserve ridge line.", "satellite_image_url": "/forest_fire_1.jpg",
            "why": ["Thermal cluster located in dense forest canopy."], "why_not": ["Not industrial flare."], "what_changed": ["Footprint expanding north."],
            "obs": [
                {"offset": 1440, "frp": 32.0, "bt": 324.0, "sensor": "VIIRS_SNPP"},
                {"offset": 720,  "frp": 38.0, "bt": 328.0, "sensor": "INSAT_3DS"},
                {"offset": 360,  "frp": 41.0, "bt": 330.0, "sensor": "VIIRS_NOAA20"},
                {"offset": 120,  "frp": 43.5, "bt": 332.0, "sensor": "INSAT_3DS"},
                {"offset": 30,   "frp": 44.8, "bt": 333.0, "sensor": "VIIRS_SNPP"},
            ],
            "evidences": [
                {"source": "NASA_FIRMS_VIIRS", "type": "Thermal", "dir": "SUPPORTING", "qual": 0.90, "rel": 0.95, "val": "FRP 44.8 MW", "exp": "Demo VIIRS detections confirm expanding vegetation fire line."}
            ]
        },

        # EVENT-SEED-004: Agricultural Burn (SAR UNAVAILABLE)
        {
            "event_id": "EVENT-SEED-004", "title": "Agricultural Burn", "location_name": "Bemetara, Chhattisgarh",
            "district": "Bemetara", "state": "Chhattisgarh", "nearby_facility": "Bemetara Rural Belt", "facility_type": "Agriculture",
            "first_detected": now - datetime.timedelta(hours=14), "last_observed": now - datetime.timedelta(hours=10),
            "centroid_lat": 21.69, "centroid_lon": 81.54, "observation_count": 3,
            "current_state": "Resolved", "source_hypothesis": "Agricultural Burn", "behavior": "Transient", "abnormality": "Normal",
            "risk_level": "Low", "risk_index": 10.0, "priority_level": "Low", "confidence": 0.85, "evidence_completeness": 0.60,
            "verification_status": "Confirmed", "frp_change_pct": -100.0, "footprint_expansion_factor": 0.0,
            "current_assessment": "Short duration post-harvest crop residue burn quenched.", "satellite_image_url": "/agri_fire_2.jpg",
            "why": ["Transient crop burning signature."], "why_not": ["Not industrial fire."], "what_changed": ["Thermal signal extinguished."],
            "obs": [
                {"offset": 840, "frp": 28.0, "bt": 322.0, "sensor": "VIIRS_SNPP"},
                {"offset": 720, "frp": 18.0, "bt": 318.0, "sensor": "INSAT_3DS"},
                {"offset": 600, "frp": 0.0,  "bt": 298.0, "sensor": "VIIRS_NOAA20"},
            ],
            "evidences": [
                {"source": "NASA_FIRMS_VIIRS", "type": "Thermal", "dir": "SUPPORTING", "qual": 0.85, "rel": 0.90, "val": "Quenched", "exp": "Demo VIIRS overpass confirms crop residue fire extinguished."}
            ]
        },

        # EVENT-SEED-007: Stubble Burning (SAR UNAVAILABLE)
        {
            "event_id": "EVENT-SEED-007", "title": "Stubble Burning", "location_name": "Ludhiana, Punjab",
            "district": "Ludhiana", "state": "Punjab", "nearby_facility": "Ludhiana Farm Belt", "facility_type": "Agriculture",
            "first_detected": now - datetime.timedelta(hours=18), "last_observed": now - datetime.timedelta(hours=12),
            "centroid_lat": 30.90, "centroid_lon": 75.85, "observation_count": 4,
            "current_state": "Resolved", "source_hypothesis": "Agricultural Burn", "behavior": "Transient", "abnormality": "Normal",
            "risk_level": "Low", "risk_index": 8.0, "priority_level": "Low", "confidence": 0.91, "evidence_completeness": 0.85,
            "verification_status": "Confirmed", "frp_change_pct": -100.0, "footprint_expansion_factor": 0.0,
            "current_assessment": "Post-harvest stubble burning verified and concluded.", "satellite_image_url": "/agri_fire_3.jpg",
            "why": ["Paddy stubble fire in agricultural parcel."], "why_not": ["Not industrial fire."], "what_changed": ["Burn completed."],
            "obs": [
                {"offset": 1080, "frp": 35.0, "bt": 325.0, "sensor": "VIIRS_SNPP"},
                {"offset": 900,  "frp": 25.0, "bt": 320.0, "sensor": "INSAT_3DS"},
                {"offset": 780,  "frp": 12.0, "bt": 310.0, "sensor": "VIIRS_NOAA20"},
                {"offset": 720,  "frp": 0.0,  "bt": 298.0, "sensor": "SENTINEL_2"},
            ],
            "evidences": [
                {"source": "NASA_FIRMS_VIIRS", "type": "Thermal", "dir": "SUPPORTING", "qual": 0.90, "rel": 0.95, "val": "Concluded", "exp": "Demo VIIRS overpass confirms stubble burn completed."}
            ]
        },

        # EVENT-SEED-009: Major Forest Fire (Simlipal National Park) (SAR AVAILABLE)
        {
            "event_id": "EVENT-SEED-009", "title": "Major Forest Fire", "location_name": "Simlipal National Park, Odisha",
            "district": "Mayurbhanj", "state": "Odisha", "nearby_facility": "Simlipal Reserve Boundary", "facility_type": "Forest",
            "first_detected": now - datetime.timedelta(days=2), "last_observed": now - datetime.timedelta(minutes=10),
            "centroid_lat": 21.93, "centroid_lon": 86.37, "observation_count": 8,
            "current_state": "Active", "source_hypothesis": "Forest Fire", "behavior": "Rapid Expansion", "abnormality": "Highly Abnormal",
            "risk_level": "High", "risk_index": 85.0, "priority_level": "High", "confidence": 0.94, "evidence_completeness": 0.88,
            "verification_status": "Needs Verification", "frp_change_pct": 210.0, "footprint_expansion_factor": 5.5,
            "current_assessment": "Rapidly spreading multi-pixel forest fire with dense smoke across multiple reserve sectors.", "satellite_image_url": "/forest_fire_2.jpg",
            "why": ["Multi-pixel forest canopy fire spreading rapidly with wind."],
            "why_not": ["No industrial facility overlap; spatial pattern is consistent with distributed vegetation burning rather than a fixed industrial source."],
            "what_changed": ["Rapid footprint expansion 5.5x with increasing thermal intensity."],
            "obs": [
                {"offset": 2880, "frp": 28.0,  "bt": 322.0, "sensor": "VIIRS_SNPP"},
                {"offset": 2160, "frp": 41.0,  "bt": 328.0, "sensor": "INSAT_3DS"},
                {"offset": 1440, "frp": 63.0,  "bt": 336.0, "sensor": "VIIRS_NOAA20"},
                {"offset": 720,  "frp": 89.0,  "bt": 345.0, "sensor": "INSAT_3DS"},
                {"offset": 360,  "frp": 117.0, "bt": 355.0, "sensor": "SENTINEL_2"},
                {"offset": 180,  "frp": 145.0, "bt": 364.0, "sensor": "VIIRS_SNPP"},
                {"offset": 60,   "frp": 173.0, "bt": 372.0, "sensor": "INSAT_3DS"},
                {"offset": 10,   "frp": 201.5, "bt": 381.0, "sensor": "VIIRS_NOAA20"},
            ],
            "evidences": [
                {"source": "NASA_FIRMS_VIIRS", "type": "Thermal", "dir": "SUPPORTING", "qual": 0.95, "rel": 0.98, "val": "Max FRP 201.5 MW", "exp": "Demo VIIRS observation: Multi-pass detections confirm expanding high-intensity canopy fire front."},
                {"source": "INSAT_3DS", "type": "Temporal", "dir": "SUPPORTING", "qual": 0.88, "rel": 0.94, "val": "Temporal Corroboration", "exp": "Synthetic INSAT-3DS demonstration data: Geostationary rapid imager tracks persistent active fire progression."},
                {"source": "SENTINEL_2", "type": "Optical", "dir": "SUPPORTING", "qual": 0.86, "rel": 0.91, "val": "Burned Vegetation & SWIR Plume", "exp": "Simulated Sentinel-2 SWIR context: 20m multi-spectral bands reveal extensive active burn scars and forward smoke plume."},
                {"source": "SENTINEL_1", "type": "SAR", "dir": "SUPPORTING", "qual": 0.82, "rel": 0.87, "val": "Canopy Structure & Burn Scar", "exp": "Synthetic Sentinel-1 SAR context: Cross-polarization backscatter change indicates forest canopy loss and burn boundary."},
                {"source": "IMD_WEATHER", "type": "Weather", "dir": "SUPPORTING", "qual": 0.82, "rel": 0.89, "val": "Wind 18 km/h SW -> NE", "exp": "Demo weather context: Surface wind driving fire line toward northeast national park sectors."},
                {"source": "OSM_GIDC_GIS", "type": "Facility", "dir": "SUPPORTING", "qual": 0.84, "rel": 0.92, "val": "Simlipal Reserve Boundary", "exp": "Demo geospatial context: No industrial facility overlap in the seeded scenario; protected biosphere reserve."},
                {"source": "HISTORICAL_FINGERPRINT", "type": "Historical", "dir": "SUPPORTING", "qual": 0.90, "rel": 0.93, "val": "5.5x Historical Reference", "exp": "Fire Radiative Power and spatial footprint exceed 99th percentile of seasonal baseline."}
            ]
        },

        # EVENT-SEED-010: Emergency Blowdown Flare (SAR UNAVAILABLE)
        {
            "event_id": "EVENT-SEED-010", "title": "Emergency Flare Spike", "location_name": "Paradip, Odisha",
            "district": "Jagatsinghpur", "state": "Odisha", "nearby_facility": "Paradip Port Industries", "facility_type": "Industrial Port",
            "first_detected": now - datetime.timedelta(hours=5), "last_observed": now - datetime.timedelta(hours=1),
            "centroid_lat": 20.26, "centroid_lon": 86.67, "observation_count": 5,
            "current_state": "Active", "source_hypothesis": "Industrial Fire", "behavior": "Sudden Spike", "abnormality": "Highly Abnormal",
            "risk_level": "High", "risk_index": 75.0, "priority_level": "High", "confidence": 0.87, "evidence_completeness": 0.75,
            "verification_status": "Needs Verification", "frp_change_pct": 150.0, "footprint_expansion_factor": 1.4,
            "current_assessment": "Sudden high-intensity flare surge indicating emergency unit depressurization.", "satellite_image_url": "/port_smoldering.jpg",
            "why": ["Sudden FRP spike at port chemical terminal."], "why_not": ["Not routine steady flare."], "what_changed": ["FRP surged +150% above baseline."],
            "obs": [
                {"offset": 300, "frp": 40.0,  "bt": 326.0, "sensor": "VIIRS_SNPP"},
                {"offset": 240, "frp": 55.0,  "bt": 332.0, "sensor": "INSAT_3DS"},
                {"offset": 180, "frp": 85.0,  "bt": 345.0, "sensor": "VIIRS_NOAA20"},
                {"offset": 120, "frp": 98.0,  "bt": 352.0, "sensor": "INSAT_3DS"},
                {"offset": 60,  "frp": 100.0, "bt": 354.0, "sensor": "SENTINEL_2"},
            ],
            "evidences": [
                {"source": "NASA_FIRMS_VIIRS", "type": "Thermal", "dir": "SUPPORTING", "qual": 0.88, "rel": 0.92, "val": "FRP 100.0 MW (+150%)", "exp": "Demo VIIRS overpasses confirm sudden high-intensity flare surge."}
            ]
        },

        # EVENT-SEED-012: Landfill Fire (SAR UNAVAILABLE)
        {
            "event_id": "EVENT-SEED-012", "title": "Landfill Fire", "location_name": "Ghazipur, Delhi",
            "district": "East Delhi", "state": "Delhi", "nearby_facility": "Ghazipur Landfill Facility", "facility_type": "Waste Management",
            "first_detected": now - datetime.timedelta(hours=24), "last_observed": now - datetime.timedelta(hours=2),
            "centroid_lat": 28.62, "centroid_lon": 77.32, "observation_count": 6,
            "current_state": "Active", "source_hypothesis": "Industrial Fire", "behavior": "Smoldering", "abnormality": "Abnormal",
            "risk_level": "Medium", "risk_index": 65.0, "priority_level": "Medium", "confidence": 0.88, "evidence_completeness": 0.78,
            "verification_status": "Needs Verification", "frp_change_pct": 50.0, "footprint_expansion_factor": 1.4,
            "current_assessment": "Persistent surface burning at waste dump site.", "satellite_image_url": "/landfill_fire.jpg",
            "why": ["Smoldering surface heat on waste dump mound."], "why_not": ["Not industrial refinery fire."], "what_changed": ["Smoke plume visible over east sector."],
            "obs": [
                {"offset": 1440, "frp": 45.0, "bt": 328.0, "sensor": "VIIRS_SNPP"},
                {"offset": 1080, "frp": 52.0, "bt": 332.0, "sensor": "INSAT_3DS"},
                {"offset": 720,  "frp": 58.0, "bt": 335.0, "sensor": "VIIRS_NOAA20"},
                {"offset": 360,  "frp": 62.0, "bt": 338.0, "sensor": "INSAT_3DS"},
                {"offset": 180,  "frp": 65.0, "bt": 340.0, "sensor": "SENTINEL_2"},
                {"offset": 120,  "frp": 67.5, "bt": 341.0, "sensor": "VIIRS_SNPP"},
            ],
            "evidences": [
                {"source": "NASA_FIRMS_VIIRS", "type": "Thermal", "dir": "SUPPORTING", "qual": 0.88, "rel": 0.90, "val": "FRP 67.5 MW", "exp": "Demo VIIRS overpasses confirm persistent landfill surface heating."}
            ]
        },

        # EVENT-SEED-013: Resolved Crop Fire (SAR UNAVAILABLE)
        {
            "event_id": "EVENT-SEED-013", "title": "Post-Harvest Field Burn", "location_name": "Karnal, Haryana",
            "district": "Karnal", "state": "Haryana", "nearby_facility": "Karnal Agricultural Belt", "facility_type": "Agriculture",
            "first_detected": now - datetime.timedelta(hours=16), "last_observed": now - datetime.timedelta(hours=4),
            "centroid_lat": 29.68, "centroid_lon": 76.99, "observation_count": 3,
            "current_state": "Resolved", "source_hypothesis": "Agricultural Burn", "behavior": "Declined and Quenched", "abnormality": "Normal",
            "risk_level": "Low", "risk_index": 5.0, "priority_level": "Low", "confidence": 0.93, "evidence_completeness": 0.82,
            "verification_status": "Confirmed", "frp_change_pct": -100.0, "footprint_expansion_factor": 0.0,
            "current_assessment": "Transient field burn extinguished on subsequent overpass.", "satellite_image_url": "/agri_fire_1.jpg",
            "why": ["Field residue burn quenched naturally."], "why_not": ["Not industrial fire."], "what_changed": ["Thermal signal 0 MW."],
            "obs": [
                {"offset": 960, "frp": 22.0, "bt": 320.0, "sensor": "VIIRS_SNPP"},
                {"offset": 480, "frp": 10.0, "bt": 308.0, "sensor": "INSAT_3DS"},
                {"offset": 240, "frp": 0.0,  "bt": 297.0, "sensor": "VIIRS_NOAA20"},
            ],
            "evidences": [
                {"source": "NASA_FIRMS_VIIRS", "type": "Thermal", "dir": "SUPPORTING", "qual": 0.92, "rel": 0.95, "val": "Quenched", "exp": "Demo VIIRS overpass confirms crop residue fire extinguished."}
            ]
        },

        # EVENT-SEED-014: Declining Industrial Hotspot (SAR AVAILABLE)
        {
            "event_id": "EVENT-SEED-014", "title": "Industrial Declining Hotspot", "location_name": "Nagpur, Maharashtra",
            "district": "Nagpur", "state": "Maharashtra", "nearby_facility": "Nagpur Industrial Zone", "facility_type": "Industrial Park",
            "first_detected": now - datetime.timedelta(hours=8), "last_observed": now - datetime.timedelta(minutes=40),
            "centroid_lat": 21.14, "centroid_lon": 79.08, "observation_count": 5,
            "current_state": "Declining", "source_hypothesis": "Industrial Fire", "behavior": "Declining", "abnormality": "Unusual",
            "risk_level": "Medium", "risk_index": 35.0, "priority_level": "Medium", "confidence": 0.86, "evidence_completeness": 0.72,
            "verification_status": "Monitoring", "frp_change_pct": -65.0, "footprint_expansion_factor": 0.7,
            "current_assessment": "Thermal output decreasing steadily (120 MW -> 15 MW). Fire suppression effective.", "satellite_image_url": "/ind_anomaly.jpg",
            "why": ["Thermal output dropping after emergency suppression."], "why_not": ["Not escalating."], "what_changed": ["FRP decreased 65%."],
            "obs": [
                {"offset": 480, "frp": 120.0, "bt": 365.0, "sensor": "VIIRS_SNPP"},
                {"offset": 360, "frp": 85.0,  "bt": 348.0, "sensor": "INSAT_3DS"},
                {"offset": 240, "frp": 50.0,  "bt": 335.0, "sensor": "VIIRS_NOAA20"},
                {"offset": 120, "frp": 25.0,  "bt": 322.0, "sensor": "INSAT_3DS"},
                {"offset": 40,  "frp": 15.0,  "bt": 318.0, "sensor": "SENTINEL_2"},
            ],
            "evidences": [
                {"source": "NASA_FIRMS_VIIRS", "type": "Thermal", "dir": "SUPPORTING", "qual": 0.88, "rel": 0.90, "val": "FRP 15.0 MW (Declining)", "exp": "Demo VIIRS overpasses confirm active thermal cooling."},
                {"source": "SENTINEL_1", "type": "SAR", "dir": "SUPPORTING", "qual": 0.85, "rel": 0.88, "val": "Structural Cooling & Stabilization", "exp": "Synthetic Sentinel-1 SAR context: Radar backscatter confirms structural stabilization and containment."}
            ]
        }
    ]

    for item in all_other_events:
        ev = Event(
            event_id=item["event_id"],
            title=item["title"],
            location_name=item["location_name"],
            district=item["district"],
            state=item["state"],
            nearby_facility=item["nearby_facility"],
            facility_type=item["facility_type"],
            first_detected=item["first_detected"],
            last_observed=item["last_observed"],
            centroid_lat=item["centroid_lat"],
            centroid_lon=item["centroid_lon"],
            observation_count=item["observation_count"],
            current_state=item["current_state"],
            source_hypothesis=item["source_hypothesis"],
            behavior=item["behavior"],
            abnormality=item["abnormality"],
            risk_level=item["risk_level"],
            risk_index=item["risk_index"],
            priority_level=item["priority_level"],
            confidence=item["confidence"],
            evidence_completeness=item["evidence_completeness"],
            verification_status=item["verification_status"],
            frp_change_pct=item["frp_change_pct"],
            footprint_expansion_factor=item["footprint_expansion_factor"],
            current_assessment=item["current_assessment"],
            satellite_image_url=item["satellite_image_url"],
            why_explanation=item["why"],
            why_not_explanation=item["why_not"],
            what_changed_explanation=item["what_changed"],
            data_mode="SEED"
        )
        db.add(ev)
        db.commit()

        # Seed Observations
        for idx, obs_item in enumerate(item["obs"], 1):
            ts = now - datetime.timedelta(minutes=obs_item["offset"])
            ob = Observation(
                source="SATELLITE_MULTI",
                source_observation_id=f"OBS-{item['event_id']}-{idx:02d}",
                latitude=item["centroid_lat"],
                longitude=item["centroid_lon"],
                timestamp=ts,
                frp=obs_item["frp"],
                brightness_temperature=obs_item["bt"],
                confidence=item["confidence"],
                satellite_sensor=obs_item["sensor"],
                spatial_resolution=375.0,
                observation_quality="NOMINAL",
                cloud_flag=obs_item.get("cloud", False),
                data_mode="SEED"
            )
            db.add(ob)
            db.commit()
            db.add(EventObservation(event_id=item["event_id"], observation_id=ob.id, sequence_number=idx))
        db.commit()

        # Seed Evidence items
        for ev_item in item["evidences"]:
            db.add(EventEvidence(
                event_id=item["event_id"],
                source=ev_item["source"],
                evidence_type=ev_item["type"],
                direction=ev_item["dir"],
                quality=ev_item["qual"],
                relevance=ev_item["rel"],
                value=ev_item["val"],
                explanation=ev_item["exp"],
                timestamp=item["last_observed"],
                data_mode="SEED"
            ))
        db.commit()

        # Seed initial Verification record for events under verification or confirmed
        db.add(VerificationRecord(
            event_id=item["event_id"],
            reviewer="Agni-Netra AI Engine",
            decision="AI Classified",
            comment=f"Auto-generated event hypothesis: {item['source_hypothesis']} ({item['current_state']}).",
            previous_status=None,
            new_status=item["verification_status"],
            timestamp=item["last_observed"],
            data_mode="SEED"
        ))
        db.commit()

    print(f"Seed data successfully injected: {db.query(Event).filter(Event.data_mode == 'SEED').count()} Events, "
          f"{db.query(Observation).filter(Observation.data_mode == 'SEED').count()} Observations, "
          f"{db.query(EventEvidence).filter(EventEvidence.data_mode == 'SEED').count()} Evidence Items, "
          f"{db.query(Facility).filter(Facility.data_mode == 'SEED').count()} Facilities.")
    db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Clear old seed data before seeding")
    args = parser.parse_args()

    print("==========================================================")
    print("  Agni-Netra: Seeding Realistic Spaceborne Demo Data")
    print("==========================================================")
    
    seed_database()
