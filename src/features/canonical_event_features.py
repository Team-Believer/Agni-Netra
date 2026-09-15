import numpy as np
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Any, List

class FeatureAvailability(str, Enum):
    ONLINE_SAFE = "ONLINE_SAFE"
    RETROSPECTIVE_ONLY = "RETROSPECTIVE_ONLY"
    CONTEXT_ONLY = "CONTEXT_ONLY"
    MODEL_DERIVED = "MODEL_DERIVED"

@dataclass
class CanonicalEventFeatures:
    """
    Canonical Event Features Schema.
    Version: AGN-FEATURES-1.1
    
    WARNING: Do NOT use RETROSPECTIVE_ONLY features in online inference!
    """
    schema_version: str = "AGN-FEATURES-1.1"
    
    # --- THERMAL ---
    current_max_frp: float = np.nan
    current_mean_frp: float = np.nan
    frp_std: float = 0.0
    recent_frp_trend: float = 0.0
    frp_change_rate: float = 0.0
    
    # --- TEMPORAL ---
    observation_count_so_far: int = 1
    event_age: float = 0.0
    persistence: float = 0.0
    observation_spacing: float = np.nan
    recent_activity: float = 0.0
    time_since_last_detection: float = np.nan
    
    # --- SPATIAL / MORPHOLOGY ---
    spatial_extent: float = 0.0
    centroid_shift: float = np.nan
    footprint_change: float = 0.0
    spatial_density: float = np.nan
    
    # --- FACILITY / CONTEXT ---
    distance_to_industrial_context: float = np.nan
    facility_context_type: int = 0
    nearby_industrial_flag: int = 0
    land_context: int = 0
    
    # --- HISTORICAL ---
    historical_event_frequency: float = 0.0
    historical_mean_frp: float = 0.0
    historical_typical_duration: float = 0.0
    historical_recurrence: float = 0.0
    historical_frp_deviation: float = np.nan
    
    # --- ANOMALY ---
    anomaly_score: float = 0.0
    change_point_indicator: int = 0
    deviation_indicators: float = 0.0
    
    # --- DATA QUALITY / MISSINGNESS ---
    observation_quality: float = 1.0
    missing_sensor_indicator: int = 0
    missing_history_indicator: int = 0
    missing_context_indicator: int = 0
    sentinel_available: int = 0
    evidence_completeness: float = 1.0
    
    # --- LOW-T / PERSISTENT THERMAL BEHAVIOR (Phase 17B) ---
    low_t_applicable: int = 0
    low_t_moderate_intensity: int = 0
    low_t_frp_level: float = np.nan
    low_t_frp_stability: float = np.nan
    low_t_persistence: float = np.nan
    low_t_recurrence: float = np.nan
    low_t_temporal_consistency: float = np.nan
    low_t_spatial_stability: float = np.nan
    low_t_recent_activity: float = np.nan
    low_t_historical_recurrence: float = np.nan
    low_t_historical_deviation: float = np.nan
    low_t_context_support: float = np.nan
    low_t_history_available: int = 0
    low_t_evidence_completeness: float = 0.0
    low_t_data_quality: float = 0.0
    
    # --- RETROSPECTIVE ONLY (LEAKAGE DANGER) ---
    retro_final_duration: float = np.nan
    retro_final_max_frp: float = np.nan

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_event_features(
    raw_event: Dict[str, Any],
    mode: str = "online"
) -> CanonicalEventFeatures:
    """
    Builds the canonical feature object from raw event data.
    
    Args:
        raw_event: Dictionary representing raw event parameters.
        mode: "online" (default) or "retrospective". 
              If "online", retro features are strictly wiped to np.nan.
    """
    features = CanonicalEventFeatures()
    
    # 1. Thermal Features
    features.current_max_frp = float(raw_event.get('current_max_frp', np.nan))
    features.current_mean_frp = float(raw_event.get('current_mean_frp', features.current_max_frp))
    features.frp_std = float(raw_event.get('frp_std', 0.0))
    features.recent_frp_trend = float(raw_event.get('recent_frp_trend', 0.0))
    features.frp_change_rate = float(raw_event.get('frp_change_rate', 0.0))
    
    # 2. Temporal Features
    features.observation_count_so_far = int(raw_event.get('observation_count_so_far', 1))
    features.event_age = float(raw_event.get('current_duration', 0.0))
    features.persistence = float(raw_event.get('persistence', features.event_age))
    features.recent_activity = float(raw_event.get('recent_activity', 0.0))
    
    if features.observation_count_so_far >= 2:
        features.observation_spacing = features.event_age / features.observation_count_so_far
        features.time_since_last_detection = float(raw_event.get('time_since_last_detection', 0.0))
    else:
        features.observation_spacing = np.nan
        features.time_since_last_detection = np.nan

    # 3. Spatial Features
    if features.observation_count_so_far >= 2:
        features.spatial_extent = float(raw_event.get('spatial_spread_km', 0.1))
        features.centroid_shift = float(raw_event.get('centroid_shift_distance_km', 0.0))
        features.footprint_change = float(raw_event.get('observation_expansion_rate', 0.0))
        features.spatial_density = features.observation_count_so_far / max(0.1, features.spatial_extent)
    else:
        features.spatial_extent = 0.0
        features.centroid_shift = np.nan
        features.footprint_change = 0.0
        features.spatial_density = np.nan
        
    # 4. Context Features
    ctx = raw_event.get('proxy_industrial_context')
    if ctx is not None:
        features.distance_to_industrial_context = float(ctx)
        features.nearby_industrial_flag = 1 if float(ctx) < 2.0 else 0
        features.missing_context_indicator = 0
    else:
        features.distance_to_industrial_context = np.nan
        features.nearby_industrial_flag = 0
        features.missing_context_indicator = 1
        
    features.facility_context_type = int(raw_event.get('facility_context_type', 0))
    features.land_context = int(raw_event.get('land_context', 0))

    # 5. Historical Features
    hist_frp = raw_event.get('hist_median_frp')
    if hist_frp is not None:
        features.historical_mean_frp = float(hist_frp)
        features.historical_frp_deviation = features.current_max_frp / max(1.0, features.historical_mean_frp) if not np.isnan(features.current_max_frp) else np.nan
        features.historical_recurrence = float(raw_event.get('historical_recurrence', 0.5))
        features.missing_history_indicator = 0
    else:
        features.missing_history_indicator = 1
        
    # 6. Anomaly Features
    features.anomaly_score = float(raw_event.get('current_vs_baseline_deviation_online', 0.0))
    features.change_point_indicator = int(raw_event.get('sudden_frp_increase', 0))
    
    # 7. Data Quality & Missingness
    s2_ndvi = raw_event.get('S2_NDVI_online')
    if s2_ndvi is not None and not np.isnan(s2_ndvi):
        features.sentinel_available = 1
    else:
        features.sentinel_available = 0
        
    features.missing_sensor_indicator = int(raw_event.get('missing_sensor_indicator', 0))
    features.observation_quality = float(raw_event.get('observation_quality', 1.0))
    
    completeness = 1.0
    if features.missing_history_indicator: completeness -= 0.25
    if features.missing_context_indicator: completeness -= 0.25
    if not features.sentinel_available: completeness -= 0.25
    if features.missing_sensor_indicator: completeness -= 0.25
    features.evidence_completeness = max(0.0, completeness)

    # 8. Retrospective Mapping
    if mode == "retrospective":
        features.retro_final_duration = float(raw_event.get('final_duration', features.event_age))
        features.retro_final_max_frp = float(raw_event.get('final_max_frp', features.current_max_frp))
    else:
        # Strictly enforce leakage protection
        features.retro_final_duration = np.nan
        features.retro_final_max_frp = np.nan

    return features
