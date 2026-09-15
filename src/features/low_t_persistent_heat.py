import numpy as np
from typing import Dict, Any, Tuple
from dataclasses import dataclass
from src.features.canonical_event_features import CanonicalEventFeatures

class LowTConfig:
    # ---------------------------------------------------------
    # Configuration / MVP Policy Thresholds
    # ---------------------------------------------------------
    MAX_FRP_FOR_LOW_T = 150.0        # Moderate thermal intensity boundary
    MIN_OBSERVATIONS = 3             # Must have some repeated detections
    MIN_PERSISTENCE_HOURS = 24.0     # Must be temporally persistent
    MAX_SPATIAL_DRIFT_KM = 2.0       # Spatial stability constraint
    MIN_TEMPORAL_CONSISTENCY = 0.2   # Fraction of expected observations
    MIN_RECURRENCE = 0.1             # Evidence of recurrent behavior
    MIN_EVIDENCE_COMPLETENESS = 0.5  # Cannot score with totally missing data

@dataclass
class LowTResult:
    low_t_state: str
    low_t_score: float
    low_t_applicable: int
    low_t_features: Dict[str, Any]
    low_t_supporting_evidence: list
    low_t_missing_evidence: list
    low_t_conflicting_evidence: list
    low_t_evidence_completeness: float
    low_t_data_quality: float

def compute_low_t_features(canon: CanonicalEventFeatures) -> None:
    """
    Populates the low_t_* namespace inside the canonical features object in-place.
    """
    # 1. Applicability / Intensity
    canon.low_t_moderate_intensity = 1 if canon.current_mean_frp <= LowTConfig.MAX_FRP_FOR_LOW_T else 0
    
    # 2. Extract mapped features (safely handling NaNs)
    canon.low_t_frp_level = canon.current_mean_frp
    canon.low_t_frp_stability = canon.frp_std if not np.isnan(canon.frp_std) else 0.0
    canon.low_t_persistence = canon.persistence
    
    # Temporal Consistency (Observations per unit persistence)
    if canon.persistence > 0:
        expected_obs = canon.persistence / 12.0 # assuming roughly 2 per day ideally
        canon.low_t_temporal_consistency = min(1.0, canon.observation_count_so_far / max(1.0, expected_obs))
    else:
        canon.low_t_temporal_consistency = 0.0
        
    canon.low_t_recent_activity = canon.recent_activity
    canon.low_t_spatial_stability = max(0.0, 1.0 - (canon.centroid_shift / LowTConfig.MAX_SPATIAL_DRIFT_KM)) if not np.isnan(canon.centroid_shift) else 1.0
    
    # Context / Historical
    canon.low_t_context_support = 1.0 if (canon.nearby_industrial_flag == 1 or canon.land_context == 1) else 0.0
    
    if canon.missing_history_indicator == 0:
        canon.low_t_history_available = 1
        canon.low_t_historical_recurrence = canon.historical_recurrence
        canon.low_t_historical_deviation = canon.historical_frp_deviation
    else:
        canon.low_t_history_available = 0
        canon.low_t_historical_recurrence = np.nan
        canon.low_t_historical_deviation = np.nan
        
    # Generalized recurrence combines recent + historical
    canon.low_t_recurrence = max(canon.low_t_historical_recurrence if not np.isnan(canon.low_t_historical_recurrence) else 0.0,
                                 canon.low_t_temporal_consistency)
    
    # Data Quality
    canon.low_t_data_quality = canon.observation_quality
    
    # Completeness (penalize if history is missing, but do not set recurrence to fake zero)
    comp = 1.0
    if canon.low_t_history_available == 0: comp -= 0.3
    if np.isnan(canon.centroid_shift): comp -= 0.1
    canon.low_t_evidence_completeness = max(0.0, comp)
    
    # Finally, determine if applicable for Low-T reasoning
    canon.low_t_applicable = 1 if (
        canon.low_t_moderate_intensity == 1 and 
        canon.observation_count_so_far >= LowTConfig.MIN_OBSERVATIONS and
        canon.low_t_persistence >= LowTConfig.MIN_PERSISTENCE_HOURS
    ) else 0

def score_low_t_persistent(canon: CanonicalEventFeatures) -> float:
    """
    Computes an interpretable intelligence/evidence score.
    Returns 0.0 to 1.0.
    """
    if canon.low_t_applicable == 0:
        return 0.0
        
    score = 0.0
    
    # Weightings (sum to 1.0)
    w_persistence = 0.3
    w_temp_cons = 0.2
    w_spatial = 0.2
    w_history = 0.2
    w_context = 0.1
    
    # 1. Persistence Contribution (caps at 5 days)
    p_score = min(1.0, canon.low_t_persistence / (LowTConfig.MIN_PERSISTENCE_HOURS * 5))
    score += w_persistence * p_score
    
    # 2. Temporal consistency
    score += w_temp_cons * canon.low_t_temporal_consistency
    
    # 3. Spatial stability
    score += w_spatial * canon.low_t_spatial_stability
    
    # 4. Historical recurrence
    if canon.low_t_history_available == 1:
        score += w_history * min(1.0, canon.low_t_historical_recurrence / LowTConfig.MIN_RECURRENCE)
    else:
        # Re-distribute weight if history missing
        multiplier = 1.0 / (1.0 - w_history)
        score *= multiplier
        
    # 5. Context
    score += w_context * canon.low_t_context_support
    
    return min(1.0, score * canon.low_t_evidence_completeness)

def classify_low_t_state(score: float, canon: CanonicalEventFeatures) -> str:
    """
    Maps score and evidence to a discrete decision state.
    """
    if canon.low_t_applicable == 0:
        return "LOW_T_NOT_APPLICABLE"
        
    if canon.low_t_evidence_completeness < LowTConfig.MIN_EVIDENCE_COMPLETENESS:
        return "LOW_T_INSUFFICIENT_EVIDENCE"
        
    if score >= 0.7:
        return "LOW_T_PERSISTENT"
    elif score >= 0.4:
        return "LOW_T_POSSIBLE"
    else:
        return "LOW_T_INSUFFICIENT_EVIDENCE"

def build_low_t_evidence(canon: CanonicalEventFeatures, state: str, score: float) -> Tuple[list, list, list]:
    """
    Generates human-readable evidence strings.
    """
    supporting = []
    missing = []
    conflicting = []
    
    if canon.low_t_applicable == 1:
        supporting.append(f"Repeated moderate thermal detections (mean FRP: {canon.current_mean_frp:.1f})")
        supporting.append(f"Temporal persistence ({canon.persistence:.1f} hours)")
        
        if canon.low_t_spatial_stability > 0.8:
            supporting.append("Stable spatial location")
        else:
            conflicting.append("Inconsistent spatial behavior (footprint expanding or shifting)")
            
        if canon.low_t_context_support > 0:
            supporting.append("Relevant facility/land context identified")
            
        if canon.low_t_history_available == 1:
            if canon.low_t_historical_recurrence > LowTConfig.MIN_RECURRENCE:
                supporting.append(f"Historically recurrent activity (recurrence: {canon.low_t_historical_recurrence:.2f})")
            else:
                conflicting.append("Little to no historical recurrence at this location")
        else:
            missing.append("Insufficient historical baseline")
            
        if canon.sentinel_available == 0:
            missing.append("Missing optical/Sentinel corroboration")
            
    else:
        if canon.low_t_moderate_intensity == 0:
            conflicting.append(f"Thermal intensity exceeds moderate bounds (FRP: {canon.current_mean_frp:.1f})")
        if canon.observation_count_so_far < LowTConfig.MIN_OBSERVATIONS:
            missing.append(f"Insufficient observations ({canon.observation_count_so_far} < {LowTConfig.MIN_OBSERVATIONS})")
        if canon.persistence < LowTConfig.MIN_PERSISTENCE_HOURS:
            conflicting.append(f"Event too brief for persistent categorization ({canon.persistence:.1f}h)")
            
    return supporting, missing, conflicting

def get_low_t_behavior_signal(canon: CanonicalEventFeatures, score: float) -> str:
    """
    Extracts a purely behavioral descriptor decoupled from source.
    """
    if canon.low_t_applicable == 0:
        return "TRANSIENT_OR_EXTREME"
    if score >= 0.7:
        if canon.low_t_recurrence > 0.5:
            return "RECURRING_PERSISTENT"
        return "STABLE_PERSISTENT"
    return "DEVELOPING_OR_TRANSIENT"

def evaluate_low_t_lane(canon: CanonicalEventFeatures) -> LowTResult:
    """
    End-to-end Low-T lane evaluation.
    """
    # 1. Compute Features In-place
    compute_low_t_features(canon)
    
    # 2. Score
    score = score_low_t_persistent(canon)
    
    # 3. Classify State
    state = classify_low_t_state(score, canon)
    
    # 4. Generate Evidence
    supp, miss, conf = build_low_t_evidence(canon, state, score)
    
    # Construct feature snapshot mapping
    features_dict = {
        "low_t_applicable": canon.low_t_applicable,
        "low_t_score": float(score),
        "low_t_frp_level": canon.low_t_frp_level,
        "low_t_persistence": canon.low_t_persistence,
        "low_t_spatial_stability": canon.low_t_spatial_stability,
        "low_t_temporal_consistency": canon.low_t_temporal_consistency,
        "low_t_recurrence": canon.low_t_recurrence,
        "low_t_context_support": canon.low_t_context_support,
        "low_t_history_available": canon.low_t_history_available
    }
    
    return LowTResult(
        low_t_state=state,
        low_t_score=score,
        low_t_applicable=canon.low_t_applicable,
        low_t_features=features_dict,
        low_t_supporting_evidence=supp,
        low_t_missing_evidence=miss,
        low_t_conflicting_evidence=conf,
        low_t_evidence_completeness=canon.low_t_evidence_completeness,
        low_t_data_quality=canon.low_t_data_quality
    )
