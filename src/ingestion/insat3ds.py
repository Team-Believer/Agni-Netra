"""
Agni-Netra INSAT-3DS High-Cadence Thermal Evidence Lane (Phase 20B)

Modular Indian Geostationary (GEO) thermal observation ingestion and cross-sensor corroboration lane.

Scientific Principles:
INSAT-3DS != GROUND TRUTH
INSAT-3DS != FIRE CONFIRMATION
INSAT-3DS != FACILITY-LEVEL LOCALIZATION
INSAT-3DS = HIGH-CADENCE THERMAL EVIDENCE / CORROBORATION

FIRMS/VIIRS remains the primary event observation backbone.
INSAT-3DS provides rapid temporal cross-checks, continuity, and corroboration.
"""

import os
import json
import math
import numpy as np
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple, Union

from src.intelligence.observation_quality import (
    evaluate_single_observation_quality, ObservationQualityAssessment,
    ObservationQualityConfig
)

# Source Sensor Constant
SENSOR_INSAT3DS = "INSAT-3DS"
PRODUCT_DEFAULT = "INSAT3DS_HEM_L2B"

# Corroboration States
CORROBORATION_CORROBORATING = "CORROBORATING"
CORROBORATION_PARTIALLY_CORROBORATING = "PARTIALLY_CORROBORATING"
CORROBORATION_CONFLICTING = "CONFLICTING"
CORROBORATION_INSUFFICIENT = "INSUFFICIENT"
CORROBORATION_NOT_AVAILABLE = "NOT_AVAILABLE"

# Freshness States
FRESHNESS_FRESH = "FRESH"
FRESHNESS_RECENT = "RECENT"
FRESHNESS_STALE = "STALE"
FRESHNESS_UNKNOWN = "UNKNOWN"

# Association States
ASSOCIATION_ALIGNED = "ALIGNED"
ASSOCIATION_AMBIGUOUS = "AMBIGUOUS_EVENT_ASSOCIATION"
ASSOCIATION_UNALIGNED = "UNALIGNED"


@dataclass
class INSAT3DSConfig:
    """Centralized thresholds and parameters for INSAT-3DS GEO lane."""
    spatial_resolution_km: float = 4.0
    max_alignment_distance_km: float = 10.0  # Coarse GEO alignment radius
    max_alignment_time_window_hours: float = 3.0
    fresh_threshold_hours: float = 1.0
    recent_threshold_hours: float = 6.0
    stale_threshold_hours: float = 24.0
    default_product: str = PRODUCT_DEFAULT


@dataclass
class SensorSourceRegistry:
    """Registry entry for satellite observation sources."""
    source_name: str
    source_type: str        # GEO, LEO, OPTICAL, SAR
    cadence_class: str      # HIGH_CADENCE_15MIN, POLAR_DAILY, POLAR_5DAY
    spatial_resolution_class: str # COARSE_GEO_4KM, MODERATE_LEO_375M, FINE_OPTICAL_10M
    latency_class: str      # RAPID_REALTIME, STANDARD_LATENCY
    available_evidence_types: List[str]


SENSOR_REGISTRY = {
    "INSAT-3DS": SensorSourceRegistry(
        source_name="INSAT-3DS",
        source_type="GEO",
        cadence_class="HIGH_CADENCE_15MIN",
        spatial_resolution_class="COARSE_GEO_4KM",
        latency_class="RAPID_REALTIME",
        available_evidence_types=["THERMAL_CONTINUITY", "BRIGHTNESS_TEMP", "TEMPORAL_ESCALATION"]
    ),
    "VIIRS": SensorSourceRegistry(
        source_name="VIIRS",
        source_type="LEO",
        cadence_class="POLAR_DAILY",
        spatial_resolution_class="MODERATE_LEO_375M",
        latency_class="STANDARD_LATENCY",
        available_evidence_types=["FRP", "BRIGHTNESS_TEMP", "SPATIAL_EXTENT"]
    ),
    "MODIS": SensorSourceRegistry(
        source_name="MODIS",
        source_type="LEO",
        cadence_class="POLAR_DAILY",
        spatial_resolution_class="MODERATE_LEO_1KM",
        latency_class="STANDARD_LATENCY",
        available_evidence_types=["FRP", "BRIGHTNESS_TEMP"]
    )
}


@dataclass
class NormalizedObservation:
    """Shared normalized observation schema across all thermal sensors."""
    observation_id: str
    source_sensor: str
    product: str
    timestamp: str
    latitude: float
    longitude: float
    brightness_temperature: Optional[float] = None
    thermal_band: Optional[str] = None
    radiance: Optional[float] = None
    frp: Optional[float] = None
    quality: Optional[float] = None
    cloud_status: Optional[str] = None
    solar_geometry: Optional[Dict[str, float]] = None
    view_geometry: Optional[Dict[str, float]] = None
    sensor_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "NormalizedObservation":
        return cls(
            observation_id=d["observation_id"],
            source_sensor=d["source_sensor"],
            product=d["product"],
            timestamp=d["timestamp"],
            latitude=float(d["latitude"]),
            longitude=float(d["longitude"]),
            brightness_temperature=float(d["brightness_temperature"]) if d.get("brightness_temperature") is not None else None,
            thermal_band=d.get("thermal_band"),
            radiance=float(d["radiance"]) if d.get("radiance") is not None else None,
            frp=float(d["frp"]) if d.get("frp") is not None else None,
            quality=float(d["quality"]) if d.get("quality") is not None else None,
            cloud_status=d.get("cloud_status"),
            solar_geometry=d.get("solar_geometry"),
            view_geometry=d.get("view_geometry"),
            sensor_metadata=d.get("sensor_metadata", {})
        )


@dataclass
class SensorCorroborationAssessment:
    event_id: str
    firms_status: Dict[str, Any]
    insat3ds_status: Dict[str, Any]
    temporal_alignment: str
    spatial_alignment: str
    corroboration_state: str
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SensorCorroborationAssessment":
        return cls(
            event_id=d["event_id"],
            firms_status=d["firms_status"],
            insat3ds_status=d["insat3ds_status"],
            temporal_alignment=d["temporal_alignment"],
            spatial_alignment=d["spatial_alignment"],
            corroboration_state=d["corroboration_state"],
            summary=d["summary"]
        )


def _haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two points in km."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def evaluate_source_freshness(timestamp_str: str, reference_time_str: Optional[str] = None, config: Optional[INSAT3DSConfig] = None) -> Tuple[str, float]:
    """
    Evaluates observation freshness category (FRESH, RECENT, STALE, UNKNOWN) and age in hours.
    """
    if config is None:
        config = INSAT3DSConfig()

    try:
        if timestamp_str.endswith("Z"):
            ts_clean = timestamp_str[:-1] + "+00:00"
        else:
            ts_clean = timestamp_str
        dt_obs = datetime.fromisoformat(ts_clean)
        if dt_obs.tzinfo is None:
            dt_obs = dt_obs.replace(tzinfo=timezone.utc)

        if reference_time_str:
            if reference_time_str.endswith("Z"):
                ref_clean = reference_time_str[:-1] + "+00:00"
            else:
                ref_clean = reference_time_str
            dt_ref = datetime.fromisoformat(ref_clean)
            if dt_ref.tzinfo is None:
                dt_ref = dt_ref.replace(tzinfo=timezone.utc)
        else:
            dt_ref = datetime.now(timezone.utc)

        age_hours = abs((dt_ref - dt_obs).total_seconds()) / 3600.0

        if age_hours <= config.fresh_threshold_hours:
            return FRESHNESS_FRESH, age_hours
        elif age_hours <= config.recent_threshold_hours:
            return FRESHNESS_RECENT, age_hours
        elif age_hours <= config.stale_threshold_hours:
            return FRESHNESS_STALE, age_hours
        else:
            return FRESHNESS_STALE, age_hours
    except Exception:
        return FRESHNESS_UNKNOWN, 0.0


def normalize_insat3ds_observation(raw_obs: Dict[str, Any], config: Optional[INSAT3DSConfig] = None) -> NormalizedObservation:
    """
    Normalizes a raw INSAT-3DS observation dictionary into a shared NormalizedObservation schema.
    Does NOT invent FRP if the product only provides brightness temperature.
    """
    if config is None:
        config = INSAT3DSConfig()

    obs_id = str(raw_obs.get("observation_id", raw_obs.get("obs_id", raw_obs.get("id", f"insat_{int(datetime.now().timestamp())}"))))
    prod = str(raw_obs.get("product", config.default_product))
    ts = str(raw_obs.get("timestamp", raw_obs.get("acq_time", raw_obs.get("time", datetime.now(timezone.utc).isoformat()))))

    lat = float(raw_obs.get("latitude", raw_obs.get("lat", np.nan)))
    lon = float(raw_obs.get("longitude", raw_obs.get("lon", np.nan)))

    bt = raw_obs.get("brightness_temperature", raw_obs.get("bright_t31", raw_obs.get("t_mir", raw_obs.get("bt"))))
    bt_float = float(bt) if bt is not None and not math.isnan(float(bt)) else None

    # FRP is only set if explicitly provided by the product (never fabricated!)
    frp_val = raw_obs.get("frp")
    frp_float = float(frp_val) if frp_val is not None and not math.isnan(float(frp_val)) else None

    cloud = str(raw_obs.get("cloud_status", raw_obs.get("cloud_cover", "UNKNOWN")))
    band = str(raw_obs.get("thermal_band", "MIR"))

    sensor_meta = dict(raw_obs)

    return NormalizedObservation(
        observation_id=obs_id,
        source_sensor=SENSOR_INSAT3DS,
        product=prod,
        timestamp=ts,
        latitude=lat,
        longitude=lon,
        brightness_temperature=bt_float,
        thermal_band=band,
        radiance=float(raw_obs.get("radiance")) if raw_obs.get("radiance") is not None else None,
        frp=frp_float,
        quality=float(raw_obs.get("quality")) if raw_obs.get("quality") is not None else None,
        cloud_status=cloud,
        sensor_metadata=sensor_meta
    )


def parse_insat3ds_file(file_content_or_path: Union[str, Dict[str, Any]], config: Optional[INSAT3DSConfig] = None) -> List[NormalizedObservation]:
    """
    Parses a local INSAT-3DS product file or dictionary payload into normalized observations.
    """
    if config is None:
        config = INSAT3DSConfig()

    raw_data = None
    if isinstance(file_content_or_path, dict):
        raw_data = file_content_or_path
    elif isinstance(file_content_or_path, str):
        if file_content_or_path.strip().startswith("{") or file_content_or_path.strip().startswith("["):
            raw_data = json.loads(file_content_or_path)
        elif os.path.exists(file_content_or_path):
            with open(file_content_or_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
        else:
            raise ValueError(f"File or JSON payload not found: {file_content_or_path}")

    obs_records = []
    if isinstance(raw_data, list):
        obs_records = raw_data
    elif isinstance(raw_data, dict):
        if "observations" in raw_data and isinstance(raw_data["observations"], list):
            obs_records = raw_data["observations"]
        else:
            obs_records = [raw_data]

    normalized_list = []
    for r in obs_records:
        norm_obs = normalize_insat3ds_observation(r, config=config)
        normalized_list.append(norm_obs)

    return normalized_list


def align_insat3ds_to_event(
    insat_obs: NormalizedObservation,
    event_centroid_lat: float,
    event_centroid_lon: float,
    event_start_time: str,
    event_end_time: Optional[str] = None,
    config: Optional[INSAT3DSConfig] = None
) -> Tuple[str, bool, float, float]:
    """
    Aligns an INSAT-3DS observation to an existing event identity based on spatial & temporal compatibility.
    Returns: (association_state, is_aligned, spatial_distance_km, temporal_delta_hours)
    """
    if config is None:
        config = INSAT3DSConfig()

    # Spatial check
    dist_km = _haversine_distance_km(insat_obs.latitude, insat_obs.longitude, event_centroid_lat, event_centroid_lon)
    spatial_compat = (dist_km <= config.max_alignment_distance_km)

    # Temporal check
    freshness, delta_hours = evaluate_source_freshness(insat_obs.timestamp, reference_time_str=event_start_time, config=config)
    temporal_compat = (delta_hours <= config.max_alignment_time_window_hours)

    if spatial_compat and temporal_compat:
        return ASSOCIATION_ALIGNED, True, round(dist_km, 2), round(delta_hours, 2)
    elif spatial_compat or temporal_compat:
        return ASSOCIATION_AMBIGUOUS, False, round(dist_km, 2), round(delta_hours, 2)
    else:
        return ASSOCIATION_UNALIGNED, False, round(dist_km, 2), round(delta_hours, 2)


def assess_sensor_corroboration(
    event_id: str,
    firms_obs_count: int,
    insat_obs_list: List[NormalizedObservation],
    event_lat: float,
    event_lon: float,
    config: Optional[INSAT3DSConfig] = None
) -> SensorCorroborationAssessment:
    """
    Computes cross-sensor corroboration assessment between FIRMS baseline and INSAT-3DS observations.
    """
    if config is None:
        config = INSAT3DSConfig()

    if not insat_obs_list:
        return SensorCorroborationAssessment(
            event_id=event_id,
            firms_status={"observation_count": firms_obs_count},
            insat3ds_status={"observation_count": 0, "availability": "UNAVAILABLE"},
            temporal_alignment="NO_INSAT_OBSERVATIONS",
            spatial_alignment="NO_INSAT_OBSERVATIONS",
            corroboration_state=CORROBORATION_NOT_AVAILABLE,
            summary="INSAT-3DS thermal evidence is unavailable for the relevant period."
        )

    aligned_count = 0
    max_bt = 0.0
    for obs in insat_obs_list:
        assoc, is_alg, dist, time_d = align_insat3ds_to_event(obs, event_lat, event_lon, obs.timestamp, config=config)
        if is_alg:
            aligned_count += 1
        if obs.brightness_temperature and obs.brightness_temperature > max_bt:
            max_bt = obs.brightness_temperature

    if aligned_count >= 2 and firms_obs_count >= 1:
        corroboration_state = CORROBORATION_CORROBORATING
        summary = "High-cadence INSAT-3DS GEO observations corroborate continued thermal activity."
    elif aligned_count == 1 and firms_obs_count >= 1:
        corroboration_state = CORROBORATION_PARTIALLY_CORROBORATING
        summary = "INSAT-3DS observation provides partial temporal corroboration for FIRMS event."
    elif aligned_count == 0 and len(insat_obs_list) > 0:
        corroboration_state = CORROBORATION_CONFLICTING
        summary = "Thermal observations from FIRMS and INSAT-3DS are not fully aligned temporally/spatially; verification is recommended."
    else:
        corroboration_state = CORROBORATION_INSUFFICIENT
        summary = "Insufficient observation count for cross-sensor corroboration."

    return SensorCorroborationAssessment(
        event_id=event_id,
        firms_status={"observation_count": firms_obs_count},
        insat3ds_status={
            "observation_count": len(insat_obs_list),
            "aligned_count": aligned_count,
            "max_brightness_temperature": max_bt,
            "availability": "AVAILABLE"
        },
        temporal_alignment="ALIGNED" if aligned_count > 0 else "MISALIGNED",
        spatial_alignment="COARSE_ALIGNED" if aligned_count > 0 else "AMBIGUOUS",
        corroboration_state=corroboration_state,
        summary=summary
    )
