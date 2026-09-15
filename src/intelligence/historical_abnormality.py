import numpy as np
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from src.features.canonical_event_features import CanonicalEventFeatures
from src.features.low_t_persistent_heat import LowTResult

class HistoricalAbnormalityConfig:
    # ---------------------------------------------------------
    # Configuration / MVP Policy Thresholds
    # ---------------------------------------------------------
    FRP_WEIGHT = 0.30
    DURATION_WEIGHT = 0.15
    FREQUENCY_WEIGHT = 0.15
    SPATIAL_WEIGHT = 0.20
    RECURRENCE_WEIGHT = 0.0
    CHANGE_WEIGHT = 0.20
    
    NORMAL_THRESHOLD = 0.25
    UNUSUAL_THRESHOLD = 0.55
    
    MINIMUM_HISTORY_EVENTS = 2
    MINIMUM_HISTORY_DAYS = 7

@dataclass
class DeviationComponents:
    frp_deviation: float
    duration_deviation: float
    frequency_deviation: float
    spatial_deviation: float
    recurrence_deviation: float
    persistence_deviation: float

@dataclass
class ChangeIndicators:
    frp_spike: int
    footprint_expansion: int
    activity_shift: int
    regime_change: int

@dataclass
class HistorySupport:
    history_tier: str
    history_available: int
    baseline_quality: float

@dataclass
class AbnormalityResult:
    abnormality_state: str
    abnormality_score: float
    supporting_evidence: List[str]
    conflicting_evidence: List[str]
    missing_evidence: List[str]
    deviation_components: DeviationComponents
    change_indicators: ChangeIndicators
    history_support: HistorySupport
    confidence: float

def compute_history_support(canon: CanonicalEventFeatures) -> HistorySupport:
    if canon.missing_history_indicator == 1:
        return HistorySupport(history_tier="HISTORY_TIER_D", history_available=0, baseline_quality=0.0)
        
    if canon.historical_event_frequency > 10 and canon.historical_recurrence > 0.5:
        return HistorySupport(history_tier="HISTORY_TIER_A", history_available=1, baseline_quality=1.0)
    elif canon.historical_event_frequency > 3:
        return HistorySupport(history_tier="HISTORY_TIER_B", history_available=1, baseline_quality=0.8)
    else:
        return HistorySupport(history_tier="HISTORY_TIER_C", history_available=1, baseline_quality=0.5)

def compute_deviations(canon: CanonicalEventFeatures, mode: str = "online") -> DeviationComponents:
    # FRP deviation: ratio of current mean to historical mean
    frp_dev = 0.0
    if canon.missing_history_indicator == 0 and not np.isnan(canon.historical_mean_frp) and canon.historical_mean_frp > 0:
        ratio = canon.current_mean_frp / max(1.0, canon.historical_mean_frp)
        # Scale: 1.0 is normal. 2.0 is highly unusual. 
        frp_dev = min(1.0, max(0.0, (ratio - 1.0) / 2.0))
        # Handle cases where FRP is suddenly very low? Usually anomaly is high FRP.
        
    # Duration/Persistence deviation
    dur_dev = 0.0
    if canon.missing_history_indicator == 0 and not np.isnan(canon.historical_typical_duration) and canon.historical_typical_duration > 0:
        # Online: we compare event_age so far. If it exceeds historical, it's anomalous.
        ratio = canon.event_age / max(1.0, canon.historical_typical_duration)
        dur_dev = min(1.0, max(0.0, (ratio - 1.2) / 2.0))

    # Frequency/Recurrence deviation
    freq_dev = 0.0
    if not np.isnan(canon.historical_event_frequency) and canon.historical_event_frequency > 0:
        freq_dev = min(1.0, max(0.0, (canon.recent_activity - canon.historical_event_frequency) / max(1.0, canon.historical_event_frequency)))

    # Spatial deviation
    spatial_dev = 0.0
    if canon.footprint_change > 1.5:  # e.g., 50% expansion
        spatial_dev = min(1.0, (canon.footprint_change - 1.0) / 2.0)

    # Persistence deviation against recent activity
    pers_dev = 0.0
    if canon.recent_activity > 0:
        pers_dev = min(1.0, canon.persistence / max(1.0, canon.recent_activity * 24.0))

    return DeviationComponents(
        frp_deviation=frp_dev,
        duration_deviation=dur_dev,
        frequency_deviation=freq_dev,
        spatial_deviation=spatial_dev,
        recurrence_deviation=0.0, # Recurrence is usually a behavior, sudden drop is a deviation but we focus on spikes for abnormality
        persistence_deviation=pers_dev
    )

def compute_change_indicators(canon: CanonicalEventFeatures) -> ChangeIndicators:
    frp_spike = 1 if canon.change_point_indicator == 1 or canon.frp_change_rate > 2.0 else 0
    footprint_expansion = 1 if canon.footprint_change > 2.0 else 0
    activity_shift = 1 if canon.recent_activity > 2.0 and canon.historical_event_frequency < 0.5 else 0
    regime_change = 1 if canon.anomaly_score > 0.8 else 0
    
    return ChangeIndicators(
        frp_spike=frp_spike,
        footprint_expansion=footprint_expansion,
        activity_shift=activity_shift,
        regime_change=regime_change
    )

def score_abnormality(
    deviations: DeviationComponents,
    changes: ChangeIndicators,
    history: HistorySupport,
    low_t_result: Optional[LowTResult] = None
) -> float:
    if history.history_available == 0:
        return 0.0
        
    score = 0.0
    
    score += HistoricalAbnormalityConfig.FRP_WEIGHT * deviations.frp_deviation
    score += HistoricalAbnormalityConfig.DURATION_WEIGHT * deviations.duration_deviation
    score += HistoricalAbnormalityConfig.FREQUENCY_WEIGHT * deviations.frequency_deviation
    score += HistoricalAbnormalityConfig.SPATIAL_WEIGHT * deviations.spatial_deviation
    score += HistoricalAbnormalityConfig.RECURRENCE_WEIGHT * deviations.recurrence_deviation
    
    change_score = max([changes.frp_spike, changes.footprint_expansion, changes.activity_shift, changes.regime_change])
    score += HistoricalAbnormalityConfig.CHANGE_WEIGHT * float(change_score)
    
    # Cap at 1.0
    return min(1.0, score)

def evaluate_abnormality(
    canon: CanonicalEventFeatures,
    low_t_result: Optional[LowTResult] = None,
    mode: str = "online"
) -> AbnormalityResult:
    """
    Evaluates how different the current thermal behavior is from what is normally expected.
    """
    history_support = compute_history_support(canon)
    deviations = compute_deviations(canon, mode=mode)
    changes = compute_change_indicators(canon)
    
    score = score_abnormality(deviations, changes, history_support, low_t_result)
    
    # Evidence generation
    supporting = []
    missing = []
    conflicting = []
    
    if history_support.history_available == 0:
        state = "UNKNOWN"
        missing.append("Insufficient history to establish a baseline.")
    else:
        if score <= HistoricalAbnormalityConfig.NORMAL_THRESHOLD:
            state = "NORMAL"
            supporting.append("Current thermal activity remains within historical range.")
        elif score <= HistoricalAbnormalityConfig.UNUSUAL_THRESHOLD:
            state = "UNUSUAL"
            supporting.append(f"Thermal behavior deviates moderately from historical baseline (Score: {score:.2f}).")
        else:
            state = "HIGHLY_ABNORMAL"
            supporting.append(f"Major deviation from expected normal behavior (Score: {score:.2f}).")
            
        if deviations.frp_deviation > 0.3:
            supporting.append(f"FRP unusually high (Ratio: {canon.current_mean_frp / max(1.0, canon.historical_mean_frp):.1f}x historical).")
        if changes.frp_spike:
            supporting.append("Sudden FRP spike detected.")
        if changes.footprint_expansion:
            supporting.append("Footprint expanded rapidly relative to historical pattern.")
        if deviations.frequency_deviation > 0.5:
            supporting.append("Detection frequency increased sharply.")
            
        if state == "NORMAL":
            if canon.historical_recurrence > 0.5:
                supporting.append("Recurrence matches seasonal/historical baseline.")
                
        # Conflicting logic (if low-t is persistent but we claim highly abnormal, maybe conflict? 
        # Actually it's perfectly fine. We just list evidence.)
        
    confidence = history_support.baseline_quality
    
    return AbnormalityResult(
        abnormality_state=state,
        abnormality_score=score,
        supporting_evidence=supporting,
        conflicting_evidence=conflicting,
        missing_evidence=missing,
        deviation_components=deviations,
        change_indicators=changes,
        history_support=history_support,
        confidence=confidence
    )
