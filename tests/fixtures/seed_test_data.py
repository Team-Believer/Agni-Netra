import sys
from pathlib import Path
import datetime
import json

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.database.database import init_db, SessionLocal
from backend.app.database.models import (
    Event, Observation, EventObservation, EventEvidence, EventPrediction,
    RiskScore, PriorityScore, Alert, DataSource, AuditLog, VerificationRecord
)
from backend.app.ml.explainability import format_event_explanations

def seed_test_database():
    """
    WARNING: TEST FIXTURE ONLY.
    DO NOT USE IN PRODUCTION.
    This script generates synthetic mock events to validate UI components during automated tests.
    """
    print("Initializing TEST fixture database...")
    init_db()
    db = SessionLocal()

    print("Clearing old demo data...")
    db.query(VerificationRecord).delete()
    db.query(Alert).delete()
    db.query(RiskScore).delete()
    db.query(PriorityScore).delete()
    db.query(EventPrediction).delete()
    db.query(EventEvidence).delete()
    db.query(EventObservation).delete()
    db.query(Observation).delete()
    db.query(Event).delete()
    db.query(DataSource).delete()
    db.query(AuditLog).delete()
    db.commit()

    print("Seeding Data Sources...")
    data_sources = [
        {"name": "NASA FIRMS (VIIRS 375m)", "source_type": "SATELLITE_LEO", "status": "ONLINE", "coverage": "India Regional", "record_count": 1420, "latency_ms": 110},
        {"name": "INSAT-3DS Rapid Imager", "source_type": "SATELLITE_GEO", "status": "ONLINE", "coverage": "Indian Subcontinent (15m)", "record_count": 8640, "latency_ms": 45},
        {"name": "ESA Sentinel-2 MSI (SWIR)", "source_type": "SATELLITE_LEO", "status": "ONLINE", "coverage": "High-Res 20m Multi-spectral", "record_count": 210, "latency_ms": 320},
        {"name": "IMD Surface & Plume Wind", "source_type": "WEATHER", "status": "ONLINE", "coverage": "National AWS Network", "record_count": 3500, "latency_ms": 80},
        {"name": "OSM & GIDC Industrial GIS", "source_type": "ANCILLARY_GIS", "status": "ONLINE", "coverage": "Pan-India Critical Assets", "record_count": 480, "latency_ms": 25},
        {"name": "ESA Sentinel-1 SAR", "source_type": "RADAR_SAR", "status": "ONLINE", "coverage": "All-weather structural radar", "record_count": 140, "latency_ms": 450},
        {"name": "TROPOMI Atmospheric Plume", "source_type": "ATMOSPHERIC", "status": "ONLINE", "coverage": "NO2 / CO trace gas", "record_count": 92, "latency_ms": 390},
        {"name": "CPCB CAAQMS Stations", "source_type": "GROUND_AIR_QUALITY", "status": "DEGRADED", "coverage": "Municipal & Industrial Air", "record_count": 450, "latency_ms": 610}
    ]
    for s in data_sources:
        db.add(DataSource(**s))
    db.commit()

    now = datetime.datetime(2024, 11, 26, 14, 32, 0)

    # 1. PRIMARY SCENARIO: EVENT-042 (Matches Reference UI Exactly)
    e42_first = datetime.datetime(2024, 11, 26, 8, 12, 0)
    e42_last = datetime.datetime(2024, 11, 26, 14, 20, 0)

    event_042 = Event(
        event_id="EVENT-042",
        title="Industrial Fire (Hypothesis)",
        location_name="Jamnagar Refinery, Gujarat",
        district="Jamnagar, Gujarat",
        state="Gujarat",
        nearby_facility="Reliance Refinery",
        facility_type="Petrochemical Complex",
        first_detected=e42_first,
        last_observed=e42_last,
        centroid_lat=23.17,
        centroid_lon=72.63,
        bounding_geojson=json.dumps({
            "type": "Polygon",
            "coordinates": [[[72.61, 23.15], [72.65, 23.15], [72.65, 23.19], [72.61, 23.19], [72.61, 23.15]]]
        }),
        observation_count=4,
        current_state="Active",
        source_hypothesis="Industrial Fire",
        behavior="Escalating rapid increase",
        abnormality="Highly Abnormal",
        risk_level="Critical",
        risk_index=82.0,
        priority_level="High", # Badge says "High Priority" and "Priority: Critical"
        confidence=0.91,
        evidence_completeness=0.74,
        verification_status="Needs Verification",
        frp_change_pct=240.0,
        footprint_expansion_factor=3.1,
        current_assessment="Strong evidence of abnormal thermal activity near industrial facility. Needs human verification.",
        satellite_image_url="https://images.unsplash.com/photo-1578328819058-b69f3a3b0f6b?auto=format&fit=crop&w=600&q=80",
        why_explanation=[
            "High thermal intensity (FRP 285 MW) inside registered petrochemical refinery perimeter.",
            "Spatial thermal footprint expanded by 3.1x across 4 consecutive satellite passes in the last 6 hours.",
            "Fire Radiative Power (FRP) escalated +240% above the 90-day facility flare baseline.",
            "Continuous multi-hour thermal persistence inconsistent with brief operational safety flaring."
        ],
        why_not_explanation=[
            "Not a Routine Flare: Significant outward spatial expansion far exceeding flare stack radius.",
            "Not Agricultural Burning: Centered squarely within heavy chemical storage / cracking unit bounds.",
            "Not Sensor Glint or Reflection: Confirmed independently across daytime VIIRS and geostationary INSAT-3DS channels."
        ],
        what_changed_explanation=[
            "FRP surged by +240% compared to typical baseline average.",
            "Thermal footprint expanded 3.1x from initial 375m detection pixel.",
            "4 high-confidence observations recorded in the last 6 hours alone."
        ]
    )
    db.add(event_042)
    db.commit()

    # Add observations for EVENT-042
    obs_e42 = [
        {"ts": datetime.datetime(2024, 11, 26, 8, 12), "lat": 23.168, "lon": 72.628, "frp": 84.2, "bt": 332.1, "sat": "VIIRS_SNPP"},
        {"ts": datetime.datetime(2024, 11, 26, 10, 30), "lat": 23.170, "lon": 72.629, "frp": 142.5, "bt": 348.5, "sat": "INSAT_3DS"},
        {"ts": datetime.datetime(2024, 11, 26, 12, 45), "lat": 23.172, "lon": 72.631, "frp": 218.0, "bt": 361.2, "sat": "SENTINEL_2"},
        {"ts": datetime.datetime(2024, 11, 26, 14, 20), "lat": 23.171, "lon": 72.632, "frp": 286.4, "bt": 374.8, "sat": "VIIRS_NOAA20"},
    ]
    for i, o in enumerate(obs_e42, 1):
        ob = Observation(
            source="SATELLITE_MULTI",
            source_observation_id=f"OBS-E42-{i:02d}",
            latitude=o["lat"],
            longitude=o["lon"],
            timestamp=o["ts"],
            frp=o["frp"],
            brightness_temperature=o["bt"],
            confidence=0.92,
            satellite_sensor=o["sat"],
            spatial_resolution=375.0,
            observation_quality="NOMINAL",
            smoke_flag=True,
            saturation_flag=o["frp"] > 250
        )
        db.add(ob)
        db.commit()
        db.add(EventObservation(event_id="EVENT-042", observation_id=ob.id, sequence_number=i))

    # Evidence for EVENT-042
    evs_42 = [
        {"source": "NASA_FIRMS_VIIRS", "evidence_type": "Thermal", "direction": "SUPPORTING", "quality": 0.95, "relevance": 1.0, "value": "Max FRP 286.4 MW", "explanation": "Successive VIIRS overpasses confirm acute escalation in thermal energy output."},
        {"source": "INSAT_3DS", "evidence_type": "Temporal", "direction": "SUPPORTING", "quality": 0.88, "relevance": 0.92, "value": "15-min persistent emission", "explanation": "Geostationary MIR band indicates persistent non-pulsing thermal release over 6 hours."},
        {"source": "SENTINEL_2", "evidence_type": "Optical", "direction": "SUPPORTING", "quality": 0.94, "relevance": 0.96, "value": "SWIR B12 peak + Thick Plume", "explanation": "20m multi-spectral SWIR reveals 3 adjacent high-temperature sub-pixel cells with visible black smoke plume."},
        {"source": "IMD_WEATHER", "evidence_type": "Weather", "direction": "SUPPORTING", "quality": 0.85, "relevance": 0.82, "value": "Wind 21 km/h @ 245° (WSW)", "explanation": "Downwind plume trajectory poses elevated exposure to eastern petrochemical storage zone."},
        {"source": "OSM_INDUSTRIAL_GIS", "evidence_type": "Facility", "direction": "SUPPORTING", "quality": 0.98, "relevance": 1.0, "value": "Reliance Jamnagar Refinery (0.3 km)", "explanation": "Direct spatial coincidence with crude distillation and catalytic cracking infrastructure."},
        {"source": "HISTORICAL_FINGERPRINT", "evidence_type": "Historical", "direction": "SUPPORTING", "quality": 0.90, "relevance": 0.95, "value": "+240% over 90-day baseline", "explanation": "Radiative output exceeds 99.8th percentile of facility operating record for past 3 years."}
    ]
    for ev in evs_42:
        db.add(EventEvidence(event_id="EVENT-042", timestamp=e42_last, **ev))

    # Alert for EVENT-042
    db.add(Alert(
        event_id="EVENT-042",
        alert_type="Industrial Thermal Escalation",
        severity="Critical",
        title="Critical Anomaly: Jamnagar Refinery, Gujarat",
        message="EVENT-042 exhibits +240% FRP surge with expanding footprint near primary processing units."
    ))

    # 2. OTHER RECENT EVENTS IN TABLE
    other_events = [
        {
            "event_id": "EVENT-041",
            "title": "Possible Wildfire",
            "location_name": "Raipur, Chhattisgarh",
            "district": "Raipur",
            "state": "Chhattisgarh",
            "nearby_facility": "Barnawapara Forest Boundary",
            "facility_type": "Forest Reserve",
            "first_detected": datetime.datetime(2024, 11, 26, 11, 15),
            "last_observed": datetime.datetime(2024, 11, 26, 13, 5),
            "centroid_lat": 21.25,
            "centroid_lon": 81.63,
            "observation_count": 3,
            "current_state": "Active",
            "source_hypothesis": "Possible Wildfire",
            "behavior": "Stable",
            "abnormality": "Normal",
            "risk_level": "Medium",
            "risk_index": 46.0,
            "priority_level": "Medium",
            "confidence": 0.78,
            "evidence_completeness": 0.65,
            "verification_status": "Monitoring",
            "frp_change_pct": 12.0,
            "footprint_expansion_factor": 1.2,
            "current_assessment": "Vegetation fire moving along ridge line. Monitoring perimeter spread."
        },
        {
            "event_id": "EVENT-040",
            "title": "Agricultural Burn",
            "location_name": "Nagpur, Maharashtra",
            "district": "Nagpur",
            "state": "Maharashtra",
            "nearby_facility": "Rural Agricultural Belt",
            "facility_type": "Farmland",
            "first_detected": datetime.datetime(2024, 11, 26, 10, 0),
            "last_observed": datetime.datetime(2024, 11, 26, 11, 48),
            "centroid_lat": 21.14,
            "centroid_lon": 79.08,
            "observation_count": 2,
            "current_state": "Active",
            "source_hypothesis": "Agricultural Burn",
            "behavior": "Transient",
            "abnormality": "Normal",
            "risk_level": "Low",
            "risk_index": 22.0,
            "priority_level": "Low",
            "confidence": 0.89,
            "evidence_completeness": 0.58,
            "verification_status": "Active",
            "frp_change_pct": -15.0,
            "footprint_expansion_factor": 1.0,
            "current_assessment": "Post-harvest crop residue burn. Rapid diurnal decay expected."
        },
        {
            "event_id": "EVENT-039",
            "title": "Unknown Thermal Signature",
            "location_name": "Paradip, Odisha",
            "district": "Paradip",
            "state": "Odisha",
            "nearby_facility": "Paradip Industrial Outskirts",
            "facility_type": "Industrial Land",
            "first_detected": datetime.datetime(2024, 11, 26, 9, 30),
            "last_observed": datetime.datetime(2024, 11, 26, 10, 12),
            "centroid_lat": 20.31,
            "centroid_lon": 86.61,
            "observation_count": 1,
            "current_state": "Detected",
            "source_hypothesis": "Unknown",
            "behavior": "Transient",
            "abnormality": "Unusual",
            "risk_level": "Medium",
            "risk_index": 38.0,
            "priority_level": "Medium",
            "confidence": 0.34,
            "evidence_completeness": 0.35,
            "verification_status": "Insufficient Data",
            "frp_change_pct": 0.0,
            "footprint_expansion_factor": 1.0,
            "current_assessment": "Sparse single-pass observation. High cloud cover. Awaiting next orbit."
        },
        {
            "event_id": "EVENT-038",
            "title": "Routine Flare",
            "location_name": "Mathura, UP",
            "district": "Mathura",
            "state": "Uttar Pradesh",
            "nearby_facility": "IOCL Mathura Refinery",
            "facility_type": "Petroleum Refinery",
            "first_detected": datetime.datetime(2024, 11, 25, 20, 0),
            "last_observed": datetime.datetime(2024, 11, 26, 8, 30),
            "centroid_lat": 27.49,
            "centroid_lon": 77.67,
            "observation_count": 8,
            "current_state": "Persistent",
            "source_hypothesis": "Routine Flare",
            "behavior": "Persistent + Stable",
            "abnormality": "Normal",
            "risk_level": "Low",
            "risk_index": 18.0,
            "priority_level": "Low",
            "confidence": 0.94,
            "evidence_completeness": 0.85,
            "verification_status": "Monitoring",
            "frp_change_pct": 2.5,
            "footprint_expansion_factor": 1.0,
            "current_assessment": "Continuous point-source flare stack within nominal operational parameters."
        },
        # Additional active events across India (to hit 12 active, 4 high priority, 3 under verification)
        {
            "event_id": "EVENT-037",
            "title": "Industrial Fire (Hypothesis)",
            "location_name": "Vizag Petrochemical Zone, AP",
            "district": "Visakhapatnam",
            "state": "Andhra Pradesh",
            "nearby_facility": "HPCL Visakh Refinery",
            "facility_type": "Petroleum Refinery",
            "first_detected": datetime.datetime(2024, 11, 26, 7, 10),
            "last_observed": datetime.datetime(2024, 11, 26, 13, 40),
            "centroid_lat": 17.68,
            "centroid_lon": 83.21,
            "observation_count": 5,
            "current_state": "Active",
            "source_hypothesis": "Industrial Fire",
            "behavior": "Escalating",
            "abnormality": "Highly Abnormal",
            "risk_level": "Critical",
            "risk_index": 79.5,
            "priority_level": "High",
            "confidence": 0.88,
            "evidence_completeness": 0.72,
            "verification_status": "Needs Verification",
            "frp_change_pct": 180.0,
            "footprint_expansion_factor": 2.4,
            "current_assessment": "Severe heat burst adjacent to chemical storage tanks. High priority review required."
        },
        {
            "event_id": "EVENT-036",
            "title": "Emergency Flare / Abnormal Blowdown",
            "location_name": "Digboi, Assam",
            "district": "Tinsukia",
            "state": "Assam",
            "nearby_facility": "IOCL Digboi Refinery",
            "facility_type": "Refinery",
            "first_detected": datetime.datetime(2024, 11, 26, 9, 15),
            "last_observed": datetime.datetime(2024, 11, 26, 12, 50),
            "centroid_lat": 27.38,
            "centroid_lon": 95.63,
            "observation_count": 3,
            "current_state": "Active",
            "source_hypothesis": "Abnormal/Emergency Flare",
            "behavior": "Sudden Spike",
            "abnormality": "Highly Abnormal",
            "risk_level": "High",
            "risk_index": 68.0,
            "priority_level": "High",
            "confidence": 0.85,
            "evidence_completeness": 0.68,
            "verification_status": "Needs Verification",
            "frp_change_pct": 140.0,
            "footprint_expansion_factor": 1.4,
            "current_assessment": "Elevated flare emissions indicating unscheduled unit depressurization."
        },
        {
            "event_id": "EVENT-035",
            "title": "Thermal Power Coal Yard Anomaly",
            "location_name": "Singrauli Basin, MP",
            "district": "Singrauli",
            "state": "Madhya Pradesh",
            "nearby_facility": "NTPC Singrauli Super Thermal",
            "facility_type": "Power Plant",
            "first_detected": datetime.datetime(2024, 11, 26, 6, 20),
            "last_observed": datetime.datetime(2024, 11, 26, 13, 10),
            "centroid_lat": 24.19,
            "centroid_lon": 82.66,
            "observation_count": 4,
            "current_state": "Active",
            "source_hypothesis": "Mining/Industrial Heat",
            "behavior": "Persistent",
            "abnormality": "Unusual",
            "risk_level": "High",
            "risk_index": 62.0,
            "priority_level": "High",
            "confidence": 0.82,
            "evidence_completeness": 0.70,
            "verification_status": "Active",
            "frp_change_pct": 75.0,
            "footprint_expansion_factor": 1.8,
            "current_assessment": "Sub-surface coal combustion detected in open stockpile sector."
        },
        {
            "event_id": "EVENT-034",
            "title": "Offshore Platform Flare",
            "location_name": "Mumbai High Offshore",
            "district": "Arabian Sea",
            "state": "Maharashtra Offshore",
            "nearby_facility": "ONGC Mumbai High South",
            "facility_type": "Offshore Platform",
            "first_detected": datetime.datetime(2024, 11, 25, 18, 0),
            "last_observed": datetime.datetime(2024, 11, 26, 14, 0),
            "centroid_lat": 19.42,
            "centroid_lon": 71.33,
            "observation_count": 6,
            "current_state": "Persistent",
            "source_hypothesis": "Routine Flare",
            "behavior": "Stable",
            "abnormality": "Normal",
            "risk_level": "Low",
            "risk_index": 15.0,
            "priority_level": "Low",
            "confidence": 0.96,
            "evidence_completeness": 0.88,
            "verification_status": "Monitoring",
            "frp_change_pct": -4.0,
            "footprint_expansion_factor": 1.0,
            "current_assessment": "Normal continuous gas separation flaring at offshore asset."
        },
        {
            "event_id": "EVENT-033",
            "title": "Bhilai Steel Slag Cooling",
            "location_name": "Durg, Chhattisgarh",
            "district": "Durg",
            "state": "Chhattisgarh",
            "nearby_facility": "Bhilai Steel Plant",
            "facility_type": "Metallurgical Works",
            "first_detected": datetime.datetime(2024, 11, 26, 8, 40),
            "last_observed": datetime.datetime(2024, 11, 26, 12, 15),
            "centroid_lat": 21.19,
            "centroid_lon": 81.38,
            "observation_count": 3,
            "current_state": "Active",
            "source_hypothesis": "Mining/Industrial Heat",
            "behavior": "Recurring",
            "abnormality": "Normal",
            "risk_level": "Medium",
            "risk_index": 32.0,
            "priority_level": "Medium",
            "confidence": 0.91,
            "evidence_completeness": 0.76,
            "verification_status": "Monitoring",
            "frp_change_pct": 8.0,
            "footprint_expansion_factor": 1.0,
            "current_assessment": "Batch molten slag discharge within metallurgical yard bounds."
        },
        {
            "event_id": "EVENT-032",
            "title": "Mangalore Petrochemical Flare",
            "location_name": "Mangaluru, Karnataka",
            "district": "Dakshina Kannada",
            "state": "Karnataka",
            "nearby_facility": "MRPL Mangalore",
            "facility_type": "Petroleum Refinery",
            "first_detected": datetime.datetime(2024, 11, 26, 5, 0),
            "last_observed": datetime.datetime(2024, 11, 26, 11, 30),
            "centroid_lat": 12.98,
            "centroid_lon": 74.83,
            "observation_count": 4,
            "current_state": "Active",
            "source_hypothesis": "Routine Flare",
            "behavior": "Stable",
            "abnormality": "Normal",
            "risk_level": "Low",
            "risk_index": 19.0,
            "priority_level": "Low",
            "confidence": 0.93,
            "evidence_completeness": 0.81,
            "verification_status": "Monitoring",
            "frp_change_pct": -1.5,
            "footprint_expansion_factor": 1.0,
            "current_assessment": "Stationary industrial flare complying with emission baseline."
        },
        {
            "event_id": "EVENT-031",
            "title": "Barmer Crude Production Flare",
            "location_name": "Barmer, Rajasthan",
            "district": "Barmer",
            "state": "Rajasthan",
            "nearby_facility": "Vedanta Cairn Oil Field",
            "facility_type": "Upstream Extraction",
            "first_detected": datetime.datetime(2024, 11, 26, 7, 30),
            "last_observed": datetime.datetime(2024, 11, 26, 13, 0),
            "centroid_lat": 25.75,
            "centroid_lon": 71.39,
            "observation_count": 3,
            "current_state": "Active",
            "source_hypothesis": "Routine Flare",
            "behavior": "Stable",
            "abnormality": "Normal",
            "risk_level": "Low",
            "risk_index": 21.0,
            "priority_level": "Low",
            "confidence": 0.92,
            "evidence_completeness": 0.75,
            "verification_status": "Active",
            "frp_change_pct": 5.0,
            "footprint_expansion_factor": 1.0,
            "current_assessment": "Routine associated petroleum gas flaring."
        }
    ]

    for ev_data in other_events:
        exp = format_event_explanations(
            source_class=ev_data["source_hypothesis"],
            confidence=ev_data["confidence"],
            behavior=ev_data["behavior"],
            abnormality=ev_data["abnormality"],
            frp_change_pct=ev_data["frp_change_pct"],
            footprint_factor=ev_data["footprint_expansion_factor"],
            duration_hours=2.0
        )
        e = Event(
            **ev_data,
            why_explanation=exp["why"],
            why_not_explanation=exp["why_not"],
            what_changed_explanation=exp["what_changed"]
        )
        db.add(e)
        db.commit()

        # Add single representative observation
        obs = Observation(
            source="NASA_FIRMS_VIIRS",
            source_observation_id=f"OBS-{ev_data['event_id']}-01",
            latitude=ev_data["centroid_lat"],
            longitude=ev_data["centroid_lon"],
            timestamp=ev_data["last_observed"],
            frp=35.0,
            brightness_temperature=325.0,
            confidence=ev_data["confidence"],
            satellite_sensor="VIIRS_SNPP",
            spatial_resolution=375.0,
            observation_quality="NOMINAL"
        )
        db.add(obs)
        db.commit()
        db.add(EventObservation(event_id=ev_data["event_id"], observation_id=obs.id, sequence_number=1))

    # 3. SEED 8 RESOLVED EVENTS (to match the KPI "Resolved (24h): 8")
    for r_idx in range(1, 9):
        res_ev = Event(
            event_id=f"EVENT-RES-{r_idx:03d}",
            title=f"Resolved Thermal Event #{r_idx}",
            location_name=f"District Sector {r_idx}, India",
            district="Sector District",
            state="India",
            nearby_facility="Agricultural / Rural Parcel",
            facility_type="Rural",
            first_detected=now - datetime.timedelta(hours=22 - r_idx),
            last_observed=now - datetime.timedelta(hours=18 - r_idx),
            centroid_lat=20.0 + r_idx * 0.8,
            centroid_lon=76.0 + r_idx * 0.9,
            observation_count=2,
            current_state="Resolved",
            source_hypothesis="Agricultural Burn",
            behavior="Declined and Quenched",
            abnormality="Normal",
            risk_level="Low",
            risk_index=12.0,
            priority_level="Low",
            confidence=0.92,
            evidence_completeness=0.80,
            verification_status="Confirmed",
            frp_change_pct=-100.0,
            footprint_expansion_factor=0.0,
            current_assessment="Thermal signature extinguished on subsequent satellite pass. Event resolved."
        )
        db.add(res_ev)
    db.commit()

    print(f"Successfully seeded TEST database with 12 active events, 8 resolved events.")
    db.close()

if __name__ == "__main__":
    seed_test_database()
