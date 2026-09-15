"""
Agni-Netra Event State Machine & Behavioral State Intelligence (Phase 20D)

Converts event timeline, persistence, Low-T behavior, High-T thermal physics, historical abnormality,
and change signals into an explicit, deterministic Event State Machine.

Core Scientific Principles:
STATE != SOURCE CLASSIFICATION
BEHAVIOR != SOURCE
ABNORMALITY != STATE
STATE != RISK / PRIORITY
OBSERVATION GAP != PHYSICAL INACTIVITY
DORMANT != CONFIRMED EXTINCTION
"""

import math
import numpy as np
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple, Union

from src.features.canonical_event_features import CanonicalEventFeatures

# State Taxonomy Constants
STATE_NEW = "NEW"
STATE_PERSISTING = "PERSISTING"
STATE_STABLE = "STABLE"
STATE_INTERMITTENT = "INTERMITTENT"
STATE_ESCALATING = "ESCALATING"
STATE_ABNORMAL = "ABNORMAL"
STATE_RESOLVING = "RESOLVING"
STATE_DORMANT = "DORMANT"
STATE_REACTIVATED = "REACTIVATED"
STATE_UNKNOWN = "UNKNOWN"

ALL_STATES = [
    STATE_NEW, STATE_PERSISTING, STATE_STABLE, STATE_INTERMITTENT,
    STATE_ESCALATING, STATE_ABNORMAL, STATE_RESOLVING,
    STATE_DORMANT, STATE_REACTIVATED, STATE_UNKNOWN
]

# Machine-Readable Reason Codes
REASON_NEW_EVENT = "NEW_EVENT"
REASON_CONTINUED_ACTIVITY = "CONTINUED_ACTIVITY"
REASON_THERMAL_STABILITY = "THERMAL_STABILITY"
REASON_THERMAL_ESCALATION = "THERMAL_ESCALATION"
REASON_FRP_INCREASE = "FRP_INCREASE"
REASON_TEMPERATURE_INCREASE = "TEMPERATURE_INCREASE"
REASON_FOOTPRINT_EXPANSION = "FOOTPRINT_EXPANSION"
REASON_CHANGE_POINT_DETECTED = "CHANGE_POINT_DETECTED"
REASON_HISTORICAL_DEVIATION = "HISTORICAL_DEVIATION"
REASON_TEMPORAL_GAPS = "TEMPORAL_GAPS"
REASON_INTERMITTENT_OBSERVATION = "INTERMITTENT_OBSERVATION"
REASON_ACTIVITY_DECLINE = "ACTIVITY_DECLINE"
REASON_OBSERVATION_GAP = "OBSERVATION_GAP"
REASON_SENSOR_UNAVAILABLE = "SENSOR_UNAVAILABLE"
REASON_DORMANCY_WINDOW_REACHED = "DORMANCY_WINDOW_REACHED"
REASON_REACTIVATION_DETECTED = "REACTIVATION_DETECTED"
REASON_INSUFFICIENT_TEMPORAL_HISTORY = "INSUFFICIENT_TEMPORAL_HISTORY"
REASON_LOW_DATA_QUALITY = "LOW_DATA_QUALITY"
REASON_STATE_AMBIGUOUS = "STATE_AMBIGUOUS"


@dataclass
class StateMachineConfig:
    """Central policy thresholds for Event State Machine."""
    min_persistence_observations: int = 3
    intermittent_gap_threshold_hours: float = 12.0
    dormancy_window_hours: float = 24.0
    escalation_frp_ratio: float = 1.5
    resolution_frp_ratio: float = 0.5
    min_history_for_abnormal: int = 5


@dataclass
class StateHistoryEntry:
    timestamp: str
    state: str
    confidence: float
    reason_codes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "StateHistoryEntry":
        return cls(
            timestamp=d["timestamp"],
            state=d["state"],
            confidence=float(d["confidence"]),
            reason_codes=d.get("reason_codes", [])
        )


@dataclass
class EventStateAssessment:
    """Structured output from Event State Machine."""
    event_id: str
    current_state: str
    current_state_confidence: float
    current_state_since: Optional[str]
    previous_state: Optional[str]
    previous_state_since: Optional[str]
    last_transition: str
    last_transition_timestamp: Optional[str]
    transition_reason_codes: List[str]
    state_history: List[Dict[str, Any]]
    evidence_items: List[Dict[str, Any]]
    provenance: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EventStateAssessment":
        return cls(
            event_id=d["event_id"],
            current_state=d["current_state"],
            current_state_confidence=float(d["current_state_confidence"]),
            current_state_since=d.get("current_state_since"),
            previous_state=d.get("previous_state"),
            previous_state_since=d.get("previous_state_since"),
            last_transition=d["last_transition"],
            last_transition_timestamp=d.get("last_transition_timestamp"),
            transition_reason_codes=d.get("transition_reason_codes", []),
            state_history=d.get("state_history", []),
            evidence_items=d.get("evidence_items", []),
            provenance=d.get("provenance", {})
        )


def _parse_time_hours(timestamp_str: Optional[str], ref_time_str: Optional[str] = None) -> float:
    """Helper to compute delta in hours between timestamps."""
    if not timestamp_str:
        return 0.0
    try:
        ts1 = timestamp_str[:-1] + "+00:00" if timestamp_str.endswith("Z") else timestamp_str
        dt1 = datetime.fromisoformat(ts1)
        if dt1.tzinfo is None:
            dt1 = dt1.replace(tzinfo=timezone.utc)

        if ref_time_str:
            ts2 = ref_time_str[:-1] + "+00:00" if ref_time_str.endswith("Z") else ref_time_str
            dt2 = datetime.fromisoformat(ts2)
            if dt2.tzinfo is None:
                dt2 = dt2.replace(tzinfo=timezone.utc)
        else:
            dt2 = datetime.now(timezone.utc)

        return abs((dt2 - dt1).total_seconds()) / 3600.0
    except Exception:
        return 0.0


def evaluate_event_state_machine(
    canon: CanonicalEventFeatures,
    low_t_result: Optional[Any] = None,
    high_t_result: Optional[Any] = None,
    abnormality_result: Optional[Any] = None,
    insat_corroboration: Optional[Any] = None,
    quality_summary: Optional[Any] = None,
    raw_event: Optional[Dict[str, Any]] = None,
    config: Optional[StateMachineConfig] = None
) -> EventStateAssessment:
    """
    Evaluates current event state and transitions deterministically based on multi-signal evidence.
    """
    if config is None:
        config = StateMachineConfig()

    raw = raw_event or {}
    event_id = str(raw.get("event_id", raw.get("id", "evt_unknown")))
    now_ts = str(raw.get("last_observation_time", raw.get("timestamp", raw.get("acq_time", "2026-09-15T12:00:00+00:00"))))

    # Extract Timeline & Historical Context
    obs_count = int(canon.observation_count_so_far)
    persistence_hours = float(getattr(canon, 'event_age', canon.persistence))
    prev_state = str(raw.get("previous_state", raw.get("prev_state", ""))) or None
    is_sensor_outage = bool(raw.get("sensor_outage", False) or raw.get("cloud_gap", False))

    time_since_last_obs = float(raw.get("time_since_last_observation_hours", 0.0))
    if "last_observation_time" in raw:
        time_since_last_obs = _parse_time_hours(raw["last_observation_time"])

    reason_codes = []
    state = STATE_UNKNOWN
    state_conf = 0.50

    # 1. Dormancy & Reactivation Check
    if prev_state == STATE_DORMANT and obs_count > 0 and time_since_last_obs < config.dormancy_window_hours:
        state = STATE_REACTIVATED
        state_conf = 0.85
        reason_codes.append(REASON_REACTIVATION_DETECTED)
    elif time_since_last_obs >= config.dormancy_window_hours and not is_sensor_outage:
        state = STATE_DORMANT
        state_conf = 0.85
        reason_codes.append(REASON_DORMANCY_WINDOW_REACHED)
    elif is_sensor_outage:
        reason_codes.append(REASON_OBSERVATION_GAP)

    # 2. If state not set by Dormancy/Reactivation:
    if state == STATE_UNKNOWN:
        # A. Temporal Sufficiency Check for NEW state
        if obs_count <= 1:
            state = STATE_NEW
            state_conf = 0.80
            reason_codes.append(REASON_NEW_EVENT)
            reason_codes.append(REASON_INSUFFICIENT_TEMPORAL_HISTORY)
        else:
            # Multi-Signal Escalation Check
            frp_max = float(canon.current_max_frp) if not np.isnan(canon.current_max_frp) else 0.0
            frp_mean = float(canon.current_mean_frp) if not np.isnan(canon.current_mean_frp) else frp_max
            
            high_t_signal = getattr(high_t_result, "high_temperature_signal", "UNKNOWN") if high_t_result else "UNKNOWN"
            abnormality_state = getattr(abnormality_result, "abnormality_state", "NORMAL") if abnormality_result else "NORMAL"
            
            has_escalation_signals = False
            if frp_max > 200.0 or high_t_signal == "STRONG":
                reason_codes.append(REASON_THERMAL_ESCALATION)
                has_escalation_signals = True
            
            if raw.get("frp_increasing", False) or (frp_mean > 0 and frp_max / frp_mean >= config.escalation_frp_ratio):
                reason_codes.append(REASON_FRP_INCREASE)
                has_escalation_signals = True

            if getattr(canon, "recent_activity", 0.0) > 0.8:
                reason_codes.append(REASON_CHANGE_POINT_DETECTED)

            # B. Abnormality Check
            if abnormality_state in ["UNUSUAL", "HIGHLY_ABNORMAL"] and obs_count >= config.min_history_for_abnormal:
                state = STATE_ABNORMAL
                state_conf = 0.85
                reason_codes.append(REASON_HISTORICAL_DEVIATION)
            elif has_escalation_signals:
                state = STATE_ESCALATING
                state_conf = 0.85
            # C. Intermittency Check
            elif raw.get("is_intermittent", False) or (obs_count >= 3 and time_since_last_obs > config.intermittent_gap_threshold_hours):
                state = STATE_INTERMITTENT
                state_conf = 0.80
                reason_codes.append(REASON_TEMPORAL_GAPS)
                reason_codes.append(REASON_INTERMITTENT_OBSERVATION)
            # D. Resolution Check
            elif raw.get("cooling_trend", False) or (frp_mean > 0 and frp_max / max(1.0, frp_mean) <= config.resolution_frp_ratio):
                state = STATE_RESOLVING
                state_conf = 0.80
                reason_codes.append(REASON_ACTIVITY_DECLINE)
            # E. Persistence / Stability Check
            elif obs_count >= config.min_persistence_observations or persistence_hours >= 12.0:
                low_t_state = getattr(low_t_result, "low_t_state", "") if low_t_result else ""
                if low_t_state == "LOW_T_PERSISTENT" or getattr(canon, "frp_std", 0.0) < 15.0:
                    state = STATE_STABLE
                    state_conf = 0.85
                    reason_codes.append(REASON_THERMAL_STABILITY)
                else:
                    state = STATE_PERSISTING
                    state_conf = 0.85
                    reason_codes.append(REASON_CONTINUED_ACTIVITY)
            else:
                state = STATE_PERSISTING
                state_conf = 0.70
                reason_codes.append(REASON_CONTINUED_ACTIVITY)

    # 3. Quality & Sensor Degradation Adjustment
    if quality_summary is not None:
        obs_qual = getattr(quality_summary, "overall_observation_quality", 1.0)
        if obs_qual < 0.5:
            state_conf = round(state_conf * 0.8, 2)
            reason_codes.append(REASON_LOW_DATA_QUALITY)

    # 4. Construct Last Transition String
    prev_st = prev_state or "INITIAL"
    transition_str = f"{prev_st} -> {state}"

    # 5. Build Compact State History
    existing_history = raw.get("state_history", [])
    new_entry = StateHistoryEntry(
        timestamp=now_ts,
        state=state,
        confidence=state_conf,
        reason_codes=sorted(list(set(reason_codes)))
    ).to_dict()

    state_history = list(existing_history) + [new_entry]

    # 6. Build Evidence Items
    evidence_items = [{
        "evidence_family": "BEHAVIOR_STATE",
        "direction": "SUPPORTING" if state in [STATE_PERSISTING, STATE_STABLE, STATE_ESCALATING, STATE_ABNORMAL] else "NEUTRAL",
        "strength": "STRONG" if state_conf >= 0.80 else "MODERATE",
        "description": f"Event state evaluates to {state} with {state_conf:.2f} state confidence ({transition_str}).",
        "source": "EventStateMachine"
    }]

    provenance = {
        "event_id": event_id,
        "obs_count": obs_count,
        "persistence_hours": persistence_hours,
        "eval_timestamp": now_ts
    }

    return EventStateAssessment(
        event_id=event_id,
        current_state=state,
        current_state_confidence=state_conf,
        current_state_since=now_ts if prev_st != state else raw.get("current_state_since", now_ts),
        previous_state=prev_state,
        previous_state_since=raw.get("previous_state_since"),
        last_transition=transition_str,
        last_transition_timestamp=now_ts,
        transition_reason_codes=sorted(list(set(reason_codes))),
        state_history=state_history,
        evidence_items=evidence_items,
        provenance=provenance
    )
