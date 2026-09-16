import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from backend.app.database.database import Base

class Observation(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source = Column(String(50), nullable=False, index=True) # e.g. FIRMS_VIIRS, INSAT_3DS
    source_observation_id = Column(String(100), nullable=True, index=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    frp = Column(Float, nullable=True) # Fire Radiative Power (MW)
    brightness_temperature = Column(Float, nullable=True) # Kelvin
    confidence = Column(Float, nullable=True) # 0.0 - 1.0 or 0 - 100
    satellite_sensor = Column(String(50), nullable=True)
    geometry_geojson = Column(Text, nullable=True)
    spatial_resolution = Column(Float, nullable=True) # in meters/km
    observation_quality = Column(String(50), default="NOMINAL")
    cloud_flag = Column(Boolean, default=False)
    smoke_flag = Column(Boolean, default=False)
    glint_flag = Column(Boolean, default=False)
    saturation_flag = Column(Boolean, default=False)
    raw_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    event_associations = relationship("EventObservation", back_populates="observation", cascade="all, delete-orphan")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. EVENT-042, EVENT-000042
    title = Column(String(200), nullable=True) # e.g. Industrial Fire (Hypothesis)
    location_name = Column(String(200), nullable=True) # e.g. Jamnagar Refinery, Gujarat
    district = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    nearby_facility = Column(String(200), nullable=True)
    facility_type = Column(String(100), nullable=True)

    first_detected = Column(DateTime, nullable=False, index=True)
    last_observed = Column(DateTime, nullable=False, index=True)
    centroid_lat = Column(Float, nullable=False)
    centroid_lon = Column(Float, nullable=False)
    bounding_geojson = Column(Text, nullable=True)
    observation_count = Column(Integer, default=1)

    current_state = Column(String(50), default="Active", index=True) # Detected, Emerging, Persistent, Escalating, Active, Declining, Resolved, Reopened
    source_hypothesis = Column(String(100), default="UNKNOWN") # Industrial Fire, Routine Flare, Agricultural Burn, Wildfire, Unknown
    behavior = Column(String(100), default="Unknown") # Persistent, Recurring, Transient, Stable, Sudden Spike, Expanding, Escalating
    abnormality = Column(String(50), default="Normal") # Normal, Unusual, Highly Abnormal, Unknown
    risk_level = Column(String(50), default="Low") # Critical, High, Medium, Low
    risk_index = Column(Float, default=0.0) # 0 - 100
    priority_level = Column(String(50), default="Monitor", index=True) # Critical, High, Medium, Low, Monitor
    confidence = Column(Float, default=0.0) # 0.0 - 1.0 (e.g. 0.91)
    evidence_completeness = Column(Float, default=0.0) # 0.0 - 1.0 (e.g. 0.74)
    verification_status = Column(String(50), default="Needs Verification", index=True) # Needs Verification, AI Classified, Analyst Reviewed, Confirmed, Rejected, Monitoring

    # Quick summary metrics
    frp_change_pct = Column(Float, nullable=True) # e.g. 240.0 (+240%)
    footprint_expansion_factor = Column(Float, nullable=True) # e.g. 3.1
    current_assessment = Column(Text, nullable=True)
    satellite_image_url = Column(String(500), nullable=True)

    # Explainability payload
    why_explanation = Column(JSON, nullable=True)
    why_not_explanation = Column(JSON, nullable=True)
    what_changed_explanation = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    observations = relationship("EventObservation", back_populates="event", cascade="all, delete-orphan")
    evidence_items = relationship("EventEvidence", back_populates="event", cascade="all, delete-orphan")
    predictions = relationship("EventPrediction", back_populates="event", cascade="all, delete-orphan")
    verifications = relationship("VerificationRecord", back_populates="event", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="event", cascade="all, delete-orphan")


class EventObservation(Base):
    __tablename__ = "event_observations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(50), ForeignKey("events.event_id", ondelete="CASCADE"), index=True, nullable=False)
    observation_id = Column(Integer, ForeignKey("observations.id", ondelete="CASCADE"), index=True, nullable=False)
    sequence_number = Column(Integer, default=1)

    event = relationship("Event", back_populates="observations")
    observation = relationship("Observation", back_populates="event_associations")


class EventFeature(Base):
    __tablename__ = "event_features"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(50), ForeignKey("events.event_id", ondelete="CASCADE"), index=True, nullable=False)
    features_json = Column(JSON, nullable=False) # 24 canonical features + spatial/contextual
    schema_version = Column(String(50), default="1.0.0")
    calculated_at = Column(DateTime, default=datetime.datetime.utcnow)


class EventEvidence(Base):
    __tablename__ = "event_evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(50), ForeignKey("events.event_id", ondelete="CASCADE"), index=True, nullable=False)
    source = Column(String(50), nullable=False) # e.g. FIRMS_VIIRS, INSAT-3DS, SENTINEL-2, OSM, IMD_WEATHER, HISTORICAL
    evidence_type = Column(String(50), nullable=False) # Thermal, Spatial, Temporal, Optical, SAR, Weather, Facility, Historical, Atmospheric, Human
    timestamp = Column(DateTime, nullable=True)
    quality = Column(Float, default=1.0) # 0.0 - 1.0
    relevance = Column(Float, default=1.0)
    direction = Column(String(50), default="SUPPORTING") # SUPPORTING, CONFLICTING, NEUTRAL, MISSING
    value = Column(String(255), nullable=True)
    explanation = Column(Text, nullable=False)

    event = relationship("Event", back_populates="evidence_items")


class EventPrediction(Base):
    __tablename__ = "event_predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(50), ForeignKey("events.event_id", ondelete="CASCADE"), index=True, nullable=False)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    predicted_class = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    probabilities_json = Column(JSON, nullable=True)
    inference_timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    event = relationship("Event", back_populates="predictions")


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(50), ForeignKey("events.event_id", ondelete="CASCADE"), index=True, nullable=False)
    risk_index = Column(Float, nullable=False) # 0 - 100
    risk_level = Column(String(50), nullable=False) # Critical, High, Medium, Low
    hazard_score = Column(Float, default=0.0)
    vulnerability_score = Column(Float, default=0.0)
    exposure_score = Column(Float, default=0.0)
    contributing_factors = Column(JSON, nullable=True)
    calculated_at = Column(DateTime, default=datetime.datetime.utcnow)


class PriorityScore(Base):
    __tablename__ = "priority_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(50), ForeignKey("events.event_id", ondelete="CASCADE"), index=True, nullable=False)
    priority_level = Column(String(50), nullable=False) # Critical, High, Medium, Low, Monitor
    score_value = Column(Float, default=0.0)
    justification = Column(Text, nullable=True)
    calculated_at = Column(DateTime, default=datetime.datetime.utcnow)


class VerificationRecord(Base):
    __tablename__ = "verification_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(50), ForeignKey("events.event_id", ondelete="CASCADE"), index=True, nullable=False)
    reviewer = Column(String(100), nullable=False) # e.g. "Ananya Sharma" / "analyst_ops_1"
    decision = Column(String(50), nullable=False) # Confirmed, Rejected, Needs More Evidence, Monitoring, False Alarm
    comment = Column(Text, nullable=True)
    previous_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    event = relationship("Event", back_populates="verifications")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(50), ForeignKey("events.event_id", ondelete="CASCADE"), index=True, nullable=True)
    alert_type = Column(String(100), nullable=False) # High Risk Flare, Abnormal Fire, Footprint Escalation, Novel Phenom
    severity = Column(String(50), nullable=False) # Critical, High, Medium, Low
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(50), default="Active") # Active, Acknowledged, Dismissed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    event = relationship("Event", back_populates="alerts")


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False) # NASA FIRMS (VIIRS), INSAT-3DS, Sentinel-2, IMD Weather, OSM
    source_type = Column(String(50), nullable=False) # SATELLITE_LEO, SATELLITE_GEO, ANCILLARY_GIS, WEATHER
    status = Column(String(50), default="ONLINE") # ONLINE, DEGRADED, OFFLINE
    last_sync = Column(DateTime, default=datetime.datetime.utcnow)
    record_count = Column(Integer, default=0)
    latency_ms = Column(Integer, default=120)
    coverage = Column(String(100), default="India Regional")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    actor = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(100), nullable=False)
    previous_state = Column(Text, nullable=True)
    new_state = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)
