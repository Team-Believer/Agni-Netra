"""
Agni-Netra Observation Quality, Saturation & Sun-Glint Defense Layer (Phase 20A)

Defensive observation quality layer that evaluates:
1. Hard validation (latitude, longitude, FRP finiteness, timestamp structure)
2. Thermal saturation & sensor non-linearity / pixel-folding conditions
3. Daytime solar-glint & reflective-surface contamination risk
4. Event-level observation quality aggregation and evidence downweighting

Core Scientific Principles:
OBSERVATION QUALITY != EVENT CLASSIFICATION
SATURATION != FIRE
GLINT RISK != FALSE POSITIVE
MISSING EVIDENCE != NEGATIVE EVIDENCE
"""

import math
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple, Union

# Quality Levels
QUALITY_GOOD = "GOOD"
QUALITY_ACCEPTABLE = "ACCEPTABLE"
QUALITY_DEGRADED = "DEGRADED"
QUALITY_POOR = "POOR"
QUALITY_UNKNOWN = "UNKNOWN"

# Quality Actions
ACTION_ACCEPT = "ACCEPT"
ACTION_FLAG = "FLAG"
ACTION_DOWNWEIGHT = "DOWNWEIGHT"
ACTION_EXCLUDE = "EXCLUDE"

# Saturation States
SATURATION_NOT_DETECTED = "NOT_DETECTED"
SATURATION_POSSIBLE = "POSSIBLE_SATURATION"
SATURATION_LIKELY = "LIKELY_SATURATION"
SATURATION_UNKNOWN = "UNKNOWN"

# Sun-Glint States
GLINT_NO_RISK = "NO_GLINT_RISK"
GLINT_LOW_RISK = "LOW_GLINT_RISK"
GLINT_MODERATE_RISK = "MODERATE_GLINT_RISK"
GLINT_HIGH_RISK = "HIGH_GLINT_RISK"
GLINT_UNKNOWN_RISK = "UNKNOWN_GLINT_RISK"

# Day/Night Period
PERIOD_DAY = "DAY"
PERIOD_NIGHT = "NIGHT"
PERIOD_UNKNOWN = "UNKNOWN"

# Reason Codes
REASON_INVALID_COORDINATES = "INVALID_COORDINATES"
REASON_MISSING_TIMESTAMP = "MISSING_TIMESTAMP"
REASON_NON_FINITE_THERMAL = "NON_FINITE_THERMAL"
REASON_MALFORMED_STRUCTURE = "MALFORMED_STRUCTURE"
REASON_THERMAL_SATURATION_POSSIBLE = "THERMAL_SATURATION_POSSIBLE"
REASON_THERMAL_SATURATION_LIKELY = "THERMAL_SATURATION_LIKELY"
REASON_THERMAL_RESPONSE_DEGRADED = "THERMAL_RESPONSE_DEGRADED"
REASON_POSSIBLE_SENSOR_NONLINEARITY = "POSSIBLE_SENSOR_NONLINEARITY"
REASON_SUN_GLINT_RISK_HIGH = "SUN_GLINT_RISK_HIGH"
REASON_POTENTIAL_REFLECTIVE_CONTAMINATION = "POTENTIAL_REFLECTIVE_CONTAMINATION"
REASON_OBSERVATION_STALE = "OBSERVATION_STALE"


@dataclass
class ObservationQualityConfig:
    """Centralized policy thresholds for observation quality defense."""
    valid_lat_min: float = -90.0
    valid_lat_max: float = 90.0
    valid_lon_min: float = -180.0
    valid_lon_max: float = 180.0
    viirs_i4_saturation_temp: float = 367.0  # Kelvin (VIIRS I4 saturation boundary)
    modis_saturation_temp: float = 500.0     # Kelvin
    extreme_frp_threshold: float = 1000.0    # MW
    glint_solar_zenith_max_day: float = 85.0 # degrees
    glint_angle_threshold_high: float = 10.0 # degrees
    glint_angle_threshold_mod: float = 20.0  # degrees
    max_allowed_missing_fields: int = 3


@dataclass
class ObservationQualityAssessment:
    observation_id: str
    quality_score: float
    quality_level: str
    action: str
    usable_for_event_detection: bool
    usable_for_classification: bool
    usable_for_evidence: bool
    recommended_weight: float
    quality_flags: List[str]
    reason_codes: List[str]
    limitations: List[str]
    saturation_state: str
    glint_risk_state: str
    observation_period: str
    raw_observation_ref: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ObservationQualityAssessment":
        return cls(
            observation_id=d["observation_id"],
            quality_score=d["quality_score"],
            quality_level=d["quality_level"],
            action=d["action"],
            usable_for_event_detection=d["usable_for_event_detection"],
            usable_for_classification=d["usable_for_classification"],
            usable_for_evidence=d["usable_for_evidence"],
            recommended_weight=d["recommended_weight"],
            quality_flags=d["quality_flags"],
            reason_codes=d["reason_codes"],
            limitations=d["limitations"],
            saturation_state=d["saturation_state"],
            glint_risk_state=d["glint_risk_state"],
            observation_period=d["observation_period"],
            raw_observation_ref=d["raw_observation_ref"]
        )


@dataclass
class EventQualitySummary:
    total_observation_count: int
    usable_observation_count: int
    degraded_observation_count: int
    excluded_observation_count: int
    overall_observation_quality: float
    quality_summary: str
    saturation_summary: str
    glint_summary: str
    critical_quality_flags: List[str]
    observation_assessments: List[ObservationQualityAssessment]

    def to_dict(self) -> Dict[str, Any]:
        res = asdict(self)
        return res

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EventQualitySummary":
        obs_assessments = [ObservationQualityAssessment.from_dict(o) for o in d.get("observation_assessments", [])]
        return cls(
            total_observation_count=d["total_observation_count"],
            usable_observation_count=d["usable_observation_count"],
            degraded_observation_count=d["degraded_observation_count"],
            excluded_observation_count=d["excluded_observation_count"],
            overall_observation_quality=d["overall_observation_quality"],
            quality_summary=d["quality_summary"],
            saturation_summary=d["saturation_summary"],
            glint_summary=d["glint_summary"],
            critical_quality_flags=d["critical_quality_flags"],
            observation_assessments=obs_assessments
        )


def evaluate_hard_validation(
    obs_dict: Dict[str, Any],
    config: Optional[ObservationQualityConfig] = None
) -> Tuple[bool, List[str], List[str]]:
    """
    Performs strict non-repairing validation on observation coordinates, thermal values, and structure.
    Returns: (is_hard_valid, reason_codes, quality_flags)
    """
    if config is None:
        config = ObservationQualityConfig()

    reasons = []
    flags = []

    # 1. Geographic Coordinates Check
    lat = obs_dict.get("latitude", obs_dict.get("lat"))
    lon = obs_dict.get("longitude", obs_dict.get("lon"))

    if lat is None or lon is None:
        reasons.append(REASON_INVALID_COORDINATES)
        flags.append("MISSING_COORDINATES")
    else:
        try:
            lat_f = float(lat)
            lon_f = float(lon)
            if math.isnan(lat_f) or math.isinf(lat_f) or not (config.valid_lat_min <= lat_f <= config.valid_lat_max):
                reasons.append(REASON_INVALID_COORDINATES)
                flags.append("LATITUDE_OUT_OF_BOUNDS")
            if math.isnan(lon_f) or math.isinf(lon_f) or not (config.valid_lon_min <= lon_f <= config.valid_lon_max):
                reasons.append(REASON_INVALID_COORDINATES)
                flags.append("LONGITUDE_OUT_OF_BOUNDS")
        except (ValueError, TypeError):
            reasons.append(REASON_INVALID_COORDINATES)
            flags.append("MALFORMED_COORDINATES")

    # 2. Thermal Value Check (FRP / Brightness Temp)
    frp_val = obs_dict.get("frp", obs_dict.get("current_max_frp", obs_dict.get("current_mean_frp")))
    if frp_val is not None:
        try:
            frp_f = float(frp_val)
            if math.isnan(frp_f) or math.isinf(frp_f) or frp_f < 0.0:
                reasons.append(REASON_NON_FINITE_THERMAL)
                flags.append("NON_FINITE_FRP_VALUE")
        except (ValueError, TypeError):
            reasons.append(REASON_NON_FINITE_THERMAL)
            flags.append("MALFORMED_FRP_VALUE")

    is_hard_valid = len(reasons) == 0
    return is_hard_valid, reasons, flags


def detect_saturation(
    obs_dict: Dict[str, Any],
    config: Optional[ObservationQualityConfig] = None
) -> Tuple[str, List[str], List[str]]:
    """
    Detects thermal saturation and sensor non-linearity conditions.
    Returns: (saturation_state, reason_codes, quality_flags)
    """
    if config is None:
        config = ObservationQualityConfig()

    reasons = []
    flags = []

    sensor = str(obs_dict.get("sensor", obs_dict.get("instrument", ""))).upper()
    bright_ti4 = obs_dict.get("bright_ti4", obs_dict.get("bright_t31", obs_dict.get("brightness", obs_dict.get("bt"))))
    frp_val = obs_dict.get("frp", obs_dict.get("current_max_frp", obs_dict.get("current_mean_frp")))

    # Extract numeric brightness temperature if available
    bt_float = None
    if bright_ti4 is not None:
        try:
            bt_float = float(bright_ti4)
        except (ValueError, TypeError):
            pass

    # Extract numeric FRP if available
    frp_float = None
    if frp_val is not None:
        try:
            frp_float = float(frp_val)
        except (ValueError, TypeError):
            pass

    # VIIRS I4 / M13 Saturation Detection
    if "VIIRS" in sensor or "I4" in str(obs_dict.get("product", "")).upper():
        if bt_float is not None and bt_float >= config.viirs_i4_saturation_temp:
            reasons.append(REASON_THERMAL_SATURATION_LIKELY)
            reasons.append(REASON_THERMAL_RESPONSE_DEGRADED)
            flags.append("VIIRS_I4_SATURATION_TEMPERATURE_EXCEEDED")
            return SATURATION_LIKELY, reasons, flags

    # General High Thermal Saturation Check
    if bt_float is not None and bt_float >= config.modis_saturation_temp:
        reasons.append(REASON_THERMAL_SATURATION_LIKELY)
        flags.append("BRIGHTNESS_TEMPERATURE_SATURATION")
        return SATURATION_LIKELY, reasons, flags

    if frp_float is not None and frp_float >= config.extreme_frp_threshold:
        reasons.append(REASON_THERMAL_SATURATION_POSSIBLE)
        flags.append("EXTREME_FRP_SATURATION_RISK")
        return SATURATION_POSSIBLE, reasons, flags

    # Pixel-folding / Non-linearity check:
    # Unusually low reported FRP despite extreme brightness temp (>360K), or zero FRP variance
    if bt_float is not None and bt_float > 360.0 and frp_float is not None and frp_float < 1.0:
        reasons.append(REASON_POSSIBLE_SENSOR_NONLINEARITY)
        flags.append("POSSIBLE_PIXEL_FOLDING_ANOMALY")
        return SATURATION_POSSIBLE, reasons, flags

    # Sensor metadata saturation flag check
    sat_flag = obs_dict.get("saturation_flag", obs_dict.get("saturated"))
    if sat_flag in [1, True, "Y", "YES", "SATURATED"]:
        reasons.append(REASON_THERMAL_SATURATION_LIKELY)
        flags.append("SENSOR_METADATA_SATURATION_FLAGGED")
        return SATURATION_LIKELY, reasons, flags

    if bt_float is None and frp_float is None:
        return SATURATION_UNKNOWN, [], []

    return SATURATION_NOT_DETECTED, [], []


def detect_sun_glint(
    obs_dict: Dict[str, Any],
    config: Optional[ObservationQualityConfig] = None
) -> Tuple[str, str, List[str], List[str]]:
    """
    Detects potential daytime sun-glint / specular reflection contamination.
    Returns: (glint_risk_state, observation_period, reason_codes, quality_flags)
    """
    if config is None:
        config = ObservationQualityConfig()

    reasons = []
    flags = []

    # 1. Determine Day / Night Period
    daynight = str(obs_dict.get("daynight", obs_dict.get("day_night", ""))).upper()
    solar_zenith = obs_dict.get("solar_zenith", obs_dict.get("solzen"))

    sz_float = None
    if solar_zenith is not None:
        try:
            sz_float = float(solar_zenith)
        except (ValueError, TypeError):
            pass

    period = PERIOD_UNKNOWN
    if daynight in ["D", "DAY"]:
        period = PERIOD_DAY
    elif daynight in ["N", "NIGHT"]:
        period = PERIOD_NIGHT
    elif sz_float is not None:
        period = PERIOD_DAY if sz_float < config.glint_solar_zenith_max_day else PERIOD_NIGHT

    # Glint risk applies ONLY during solar illumination (DAY)
    if period == PERIOD_NIGHT:
        return GLINT_NO_RISK, PERIOD_NIGHT, [], []

    # 2. Check Glint Angle or Reflectance Metadata
    glint_angle = obs_dict.get("glint_angle", obs_dict.get("specular_angle"))
    reflectance = obs_dict.get("reflectance", obs_dict.get("reflectance_b2"))

    ga_float = None
    if glint_angle is not None:
        try:
            ga_float = float(glint_angle)
        except (ValueError, TypeError):
            pass

    ref_float = None
    if reflectance is not None:
        try:
            ref_float = float(reflectance)
        except (ValueError, TypeError):
            pass

    if ga_float is not None:
        if ga_float <= config.glint_angle_threshold_high:
            reasons.append(REASON_SUN_GLINT_RISK_HIGH)
            reasons.append(REASON_POTENTIAL_REFLECTIVE_CONTAMINATION)
            flags.append("HIGH_SUN_GLINT_GEOMETRY_ANGLE")
            return GLINT_HIGH_RISK, period, reasons, flags
        elif ga_float <= config.glint_angle_threshold_mod:
            reasons.append(REASON_POTENTIAL_REFLECTIVE_CONTAMINATION)
            flags.append("MODERATE_SUN_GLINT_GEOMETRY_ANGLE")
            return GLINT_MODERATE_RISK, period, reasons, flags
        else:
            return GLINT_NO_RISK, period, [], []

    if ref_float is not None and ref_float > 0.4:
        reasons.append(REASON_POTENTIAL_REFLECTIVE_CONTAMINATION)
        flags.append("HIGH_SURFACE_REFLECTANCE_CONTAMINATION")
        return GLINT_MODERATE_RISK, period, reasons, flags

    glint_flag = obs_dict.get("glint_flag", obs_dict.get("sun_glint"))
    if glint_flag in [1, True, "Y", "YES", "GLINT"]:
        reasons.append(REASON_SUN_GLINT_RISK_HIGH)
        reasons.append(REASON_POTENTIAL_REFLECTIVE_CONTAMINATION)
        flags.append("SENSOR_METADATA_GLINT_FLAGGED")
        return GLINT_HIGH_RISK, period, reasons, flags

    # If geometry/optical data is unavailable, return UNKNOWN_GLINT_RISK without fabricating glint evidence!
    return GLINT_UNKNOWN_RISK, period, [], []


def evaluate_single_observation_quality(
    obs_dict: Dict[str, Any],
    obs_id: Optional[str] = None,
    config: Optional[ObservationQualityConfig] = None
) -> ObservationQualityAssessment:
    """
    Evaluates observation quality, saturation, and glint for a single observation dictionary.
    """
    if config is None:
        config = ObservationQualityConfig()

    if obs_id is None:
        obs_id = str(obs_dict.get("observation_id", obs_dict.get("obs_id", obs_dict.get("id", "obs_001"))))

    # 1. Hard Validation
    is_hard_valid, hard_reasons, hard_flags = evaluate_hard_validation(obs_dict, config)

    # 2. Saturation Defense
    sat_state, sat_reasons, sat_flags = detect_saturation(obs_dict, config)

    # 3. Sun-Glint Defense
    glint_state, period, glint_reasons, glint_flags = detect_sun_glint(obs_dict, config)

    # Combine reason codes & quality flags
    all_reasons = sorted(list(set(hard_reasons + sat_reasons + glint_reasons)))
    all_flags = sorted(list(set(hard_flags + sat_flags + glint_flags)))
    limitations = []

    # Calculate Quality Score & Usability
    if not is_hard_valid:
        quality_score = 0.0
        quality_level = QUALITY_POOR
        action = ACTION_EXCLUDE
        usable_detection = False
        usable_classification = False
        usable_evidence = False
        recommended_weight = 0.0
        limitations.append(f"Hard validation failed: {', '.join(hard_flags)}")
    else:
        score = 1.0
        # Saturation penalty
        if sat_state == SATURATION_LIKELY:
            score -= 0.35
            limitations.append("Thermal saturation likely: thermal intensity accuracy degraded")
        elif sat_state == SATURATION_POSSIBLE:
            score -= 0.20
            limitations.append("Thermal saturation possible")

        # Glint penalty
        if glint_state == GLINT_HIGH_RISK:
            score -= 0.30
            limitations.append("High solar glint contamination risk")
        elif glint_state == GLINT_MODERATE_RISK:
            score -= 0.15
            limitations.append("Moderate solar glint contamination risk")

        quality_score = max(0.0, min(1.0, score))

        # Assign Quality Level & Action
        if quality_score >= 0.85:
            quality_level = QUALITY_GOOD
            action = ACTION_ACCEPT
            usable_detection = True
            usable_classification = True
            usable_evidence = True
            recommended_weight = 1.0
        elif quality_score >= 0.60:
            quality_level = QUALITY_ACCEPTABLE
            action = ACTION_FLAG
            usable_detection = True
            usable_classification = True
            usable_evidence = True
            recommended_weight = 0.85
        elif quality_score >= 0.35:
            quality_level = QUALITY_DEGRADED
            action = ACTION_DOWNWEIGHT
            usable_detection = True
            usable_classification = False  # Downweighted for source classification
            usable_evidence = True
            recommended_weight = 0.50
        else:
            quality_level = QUALITY_POOR
            action = ACTION_DOWNWEIGHT
            usable_detection = True
            usable_classification = False
            usable_evidence = False
            recommended_weight = 0.20

    return ObservationQualityAssessment(
        observation_id=obs_id,
        quality_score=quality_score,
        quality_level=quality_level,
        action=action,
        usable_for_event_detection=usable_detection,
        usable_for_classification=usable_classification,
        usable_for_evidence=usable_evidence,
        recommended_weight=recommended_weight,
        quality_flags=all_flags,
        reason_codes=all_reasons,
        limitations=limitations,
        saturation_state=sat_state,
        glint_risk_state=glint_state,
        observation_period=period,
        raw_observation_ref=dict(obs_dict)  # Preserves raw data unmutated
    )


def evaluate_event_observation_quality(
    raw_event_or_obs_list: Union[Dict[str, Any], List[Dict[str, Any]]],
    config: Optional[ObservationQualityConfig] = None
) -> EventQualitySummary:
    """
    Aggregates observation quality assessments across all observations in an event.
    """
    if config is None:
        config = ObservationQualityConfig()

    obs_list: List[Dict[str, Any]] = []
    if isinstance(raw_event_or_obs_list, list):
        obs_list = raw_event_or_obs_list
    elif isinstance(raw_event_or_obs_list, dict):
        if "observations" in raw_event_or_obs_list and isinstance(raw_event_or_obs_list["observations"], list):
            obs_list = raw_event_or_obs_list["observations"]
        else:
            # Single event dict passed as observation proxy
            obs_list = [raw_event_or_obs_list]

    assessments = []
    for i, obs in enumerate(obs_list):
        obs_id = str(obs.get("observation_id", obs.get("obs_id", f"obs_{i+1}")))
        assessments.append(evaluate_single_observation_quality(obs, obs_id=obs_id, config=config))

    total_count = len(assessments)
    usable_count = sum(1 for a in assessments if a.usable_for_event_detection and a.action != ACTION_EXCLUDE)
    degraded_count = sum(1 for a in assessments if a.quality_level in [QUALITY_DEGRADED, QUALITY_POOR])
    excluded_count = sum(1 for a in assessments if a.action == ACTION_EXCLUDE)

    if total_count > 0:
        overall_quality = float(np.mean([a.quality_score for a in assessments]))
    else:
        overall_quality = 0.0

    # Aggregate summaries
    sat_states = set(a.saturation_state for a in assessments)
    glint_states = set(a.glint_risk_state for a in assessments)
    critical_flags = sorted(list(set(f for a in assessments for f in a.quality_flags)))

    if SATURATION_LIKELY in sat_states:
        sat_sum = "Likely thermal saturation detected in one or more observations"
    elif SATURATION_POSSIBLE in sat_states:
        sat_sum = "Possible thermal saturation risk identified"
    else:
        sat_sum = "No thermal saturation detected"

    if GLINT_HIGH_RISK in glint_states:
        glint_sum = "High solar glint contamination risk identified"
    elif GLINT_MODERATE_RISK in glint_states:
        glint_sum = "Moderate solar glint contamination risk identified"
    elif GLINT_NO_RISK in glint_states:
        glint_sum = "No solar glint risk detected"
    else:
        glint_sum = "Solar glint risk status unknown"

    quality_sum = f"Event observation quality is {QUALITY_GOOD if overall_quality >= 0.85 else (QUALITY_ACCEPTABLE if overall_quality >= 0.60 else QUALITY_DEGRADED)} ({usable_count}/{total_count} usable detections)."

    return EventQualitySummary(
        total_observation_count=total_count,
        usable_observation_count=usable_count,
        degraded_observation_count=degraded_count,
        excluded_observation_count=excluded_count,
        overall_observation_quality=overall_quality,
        quality_summary=quality_sum,
        saturation_summary=sat_sum,
        glint_summary=glint_sum,
        critical_quality_flags=critical_flags,
        observation_assessments=assessments
    )
