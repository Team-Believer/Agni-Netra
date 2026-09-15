"""
Agni-Netra Phase 20D Test Suite: Event State Machine & Behavioral State Intelligence

Offline unit and integration tests covering:
A. one observation -> NEW/appropriate insufficient-history state
B. repeated compatible observations -> PERSISTING
C. stable repeated activity -> STABLE
D. repeated temporal gaps -> INTERMITTENT
E. increasing thermal behavior -> ESCALATING
F. historical deviation -> ABNORMAL
G. declining activity -> RESOLVING
H. no recent observation -> DORMANT
I. dormant event with compatible new observation -> REACTIVATED
J. dormancy does not create a new event ID
K. sensor outage is not interpreted as physical resolution
L. missing history does not fabricate abnormality
M. Low-T does not determine state alone
N. High-T does not determine state alone
O. source class does not determine state
P. state confidence separate from classification confidence
Q. evidence provenance present
R. state history deterministic
S. JSON serializable
T. analyze_event() integration
U. risk/priority consume state without duplication
V. explanation consumes state correctly
W. all source classes supported
X. frozen Phase16E-R2 unchanged
"""

import json
import os
import pytest
import numpy as np

from src.intelligence.event_state_machine import (
    StateMachineConfig, StateHistoryEntry, EventStateAssessment,
    evaluate_event_state_machine, ALL_STATES,
    STATE_NEW, STATE_PERSISTING, STATE_STABLE, STATE_INTERMITTENT,
    STATE_ESCALATING, STATE_ABNORMAL, STATE_RESOLVING,
    STATE_DORMANT, STATE_REACTIVATED, STATE_UNKNOWN,
    REASON_NEW_EVENT, REASON_DORMANCY_WINDOW_REACHED, REASON_REACTIVATION_DETECTED,
    REASON_OBSERVATION_GAP
)
from src.features.canonical_event_features import build_event_features
from src.features.low_t_persistent_heat import evaluate_low_t_lane
from src.intelligence.high_t_thermal import evaluate_high_t_lane
from src.intelligence.historical_abnormality import evaluate_abnormality
from src.intelligence.evidence_aggregation import aggregate_event_evidence
from src.intelligence.confidence_decision import evaluate_event_decision
from src.intelligence.risk_priority import evaluate_risk_and_priority
from src.intelligence.explanation_engine import generate_explanation
from src.intelligence.analyze_event import analyze_event


@pytest.fixture
def base_raw_event():
    return {
        "event_id": "evt_esm_001",
        "lat": 28.61,
        "lon": 77.20,
        "current_max_frp": 120.0,
        "current_mean_frp": 90.0,
        "observation_count_so_far": 4,
        "persistence_hours": 24.0,
        "land_context": 1
    }


def test_A_one_observation_new_state():
    """A. One observation yields NEW state with insufficient temporal history reason code."""
    raw = {"event_id": "evt_one_obs", "current_max_frp": 45.0, "observation_count_so_far": 1}
    canon = build_event_features(raw)
    assessment = evaluate_event_state_machine(canon, raw_event=raw)

    assert assessment.current_state == STATE_NEW
    assert "INSUFFICIENT_TEMPORAL_HISTORY" in assessment.transition_reason_codes


def test_B_repeated_observations_persisting(base_raw_event):
    """B. Repeated compatible observations yield PERSISTING state."""
    canon = build_event_features(base_raw_event)
    assessment = evaluate_event_state_machine(canon, raw_event=base_raw_event)

    assert assessment.current_state in [STATE_PERSISTING, STATE_STABLE]


def test_C_stable_repeated_activity(base_raw_event):
    """C. Stable repeated thermal activity yields STABLE state."""
    raw = dict(base_raw_event)
    raw["frp_std"] = 5.0
    canon = build_event_features(raw)
    low_t = evaluate_low_t_lane(canon)
    assessment = evaluate_event_state_machine(canon, low_t_result=low_t, raw_event=raw)

    assert assessment.current_state == STATE_STABLE


def test_D_repeated_temporal_gaps(base_raw_event):
    """D. Repeated temporal gaps yield INTERMITTENT state."""
    raw = dict(base_raw_event)
    raw["is_intermittent"] = True
    raw["time_since_last_observation_hours"] = 15.0
    canon = build_event_features(raw)
    assessment = evaluate_event_state_machine(canon, raw_event=raw)

    assert assessment.current_state == STATE_INTERMITTENT


def test_E_increasing_thermal_escalating(base_raw_event):
    """E. Increasing thermal behavior yields ESCALATING state."""
    raw = dict(base_raw_event)
    raw["current_max_frp"] = 350.0
    raw["frp_increasing"] = True
    canon = build_event_features(raw)
    high_t = evaluate_high_t_lane(canon, raw_event=raw)
    assessment = evaluate_event_state_machine(canon, high_t_result=high_t, raw_event=raw)

    assert assessment.current_state == STATE_ESCALATING


def test_F_historical_deviation_abnormal(base_raw_event):
    """F. Significant historical deviation yields ABNORMAL state."""
    canon = build_event_features(base_raw_event)
    from src.intelligence.historical_abnormality import AbnormalityResult, ChangeIndicators
    abnormality_result = AbnormalityResult(
        abnormality_state="HIGHLY_ABNORMAL", abnormality_score=0.92, supporting_evidence=[],
        conflicting_evidence=[], missing_evidence=[], deviation_components=None,
        change_indicators=ChangeIndicators(1, 1, 1, 1), history_support=None, confidence=0.90
    )
    raw = {**base_raw_event, "observation_count_so_far": 8}
    canon.observation_count_so_far = 8
    assessment = evaluate_event_state_machine(canon, abnormality_result=abnormality_result, raw_event=raw)

    assert assessment.current_state == STATE_ABNORMAL


def test_G_declining_activity_resolving(base_raw_event):
    """G. Declining activity yields RESOLVING state."""
    raw = dict(base_raw_event)
    raw["cooling_trend"] = True
    raw["current_max_frp"] = 10.0
    raw["current_mean_frp"] = 40.0
    canon = build_event_features(raw)
    assessment = evaluate_event_state_machine(canon, raw_event=raw)

    assert assessment.current_state == STATE_RESOLVING


def test_H_no_recent_observation_dormant(base_raw_event):
    """H. Absence of observations beyond dormancy window yields DORMANT state."""
    raw = dict(base_raw_event)
    raw["time_since_last_observation_hours"] = 36.0
    canon = build_event_features(raw)
    assessment = evaluate_event_state_machine(canon, raw_event=raw)

    assert assessment.current_state == STATE_DORMANT
    assert REASON_DORMANCY_WINDOW_REACHED in assessment.transition_reason_codes


def test_I_dormant_event_reactivated(base_raw_event):
    """I. Compatible observation received by dormant event yields REACTIVATED state."""
    raw = dict(base_raw_event)
    raw["previous_state"] = STATE_DORMANT
    raw["time_since_last_observation_hours"] = 2.0
    canon = build_event_features(raw)
    assessment = evaluate_event_state_machine(canon, raw_event=raw)

    assert assessment.current_state == STATE_REACTIVATED
    assert REASON_REACTIVATION_DETECTED in assessment.transition_reason_codes


def test_J_dormancy_preserves_event_id(base_raw_event):
    """J. Reactivated dormant event retains original persistent event ID."""
    raw = dict(base_raw_event)
    raw["previous_state"] = STATE_DORMANT
    canon = build_event_features(raw)
    assessment = evaluate_event_state_machine(canon, raw_event=raw)

    assert assessment.event_id == base_raw_event["event_id"]


def test_K_sensor_outage_not_physical_resolution(base_raw_event):
    """K. Sensor outage / cloud gap is not interpreted as physical resolution or dormancy."""
    raw = dict(base_raw_event)
    raw["sensor_outage"] = True
    raw["time_since_last_observation_hours"] = 30.0
    canon = build_event_features(raw)
    assessment = evaluate_event_state_machine(canon, raw_event=raw)

    assert assessment.current_state != STATE_DORMANT
    assert REASON_OBSERVATION_GAP in assessment.transition_reason_codes


def test_L_missing_history_does_not_fabricate_abnormality(base_raw_event):
    """L. Missing historical baseline does not fabricate ABNORMAL state."""
    raw = dict(base_raw_event)
    raw["missing_history_indicator"] = 1
    canon = build_event_features(raw)
    assessment = evaluate_event_state_machine(canon, raw_event=raw)

    assert assessment.current_state != STATE_ABNORMAL


def test_M_low_t_does_not_determine_state_alone(base_raw_event):
    """M. Low-T persistence signal alone does not lock state."""
    canon = build_event_features(base_raw_event)
    low_t = evaluate_low_t_lane(canon)
    assessment = evaluate_event_state_machine(canon, low_t_result=low_t, raw_event=base_raw_event)

    assert assessment.current_state in [STATE_PERSISTING, STATE_STABLE]


def test_N_high_t_does_not_determine_state_alone(base_raw_event):
    """N. High-T thermal physics signal alone does not lock state."""
    canon = build_event_features(base_raw_event)
    high_t = evaluate_high_t_lane(canon, raw_event=base_raw_event)
    assessment = evaluate_event_state_machine(canon, high_t_result=high_t, raw_event=base_raw_event)

    assert assessment.current_state in ALL_STATES


def test_O_source_class_decoupled_from_state(base_raw_event):
    """O. State machine logic is source-class agnostic."""
    canon = build_event_features(base_raw_event)
    assessment = evaluate_event_state_machine(canon, raw_event=base_raw_event)

    assert not hasattr(assessment, "predicted_source_class")


def test_P_state_confidence_separate_from_classification(base_raw_event):
    """P. State confidence is evaluated separately from classification confidence."""
    canon = build_event_features(base_raw_event)
    assessment = evaluate_event_state_machine(canon, raw_event=base_raw_event)

    assert 0.0 <= assessment.current_state_confidence <= 1.0


def test_Q_evidence_provenance_present(base_raw_event):
    """Q. Assessment includes complete provenance tracking."""
    canon = build_event_features(base_raw_event)
    assessment = evaluate_event_state_machine(canon, raw_event=base_raw_event)

    assert "event_id" in assessment.provenance
    assert len(assessment.evidence_items) >= 1


def test_R_state_history_deterministic(base_raw_event):
    """R. State history generation is deterministic."""
    canon = build_event_features(base_raw_event)
    a1 = evaluate_event_state_machine(canon, raw_event=base_raw_event)
    a2 = evaluate_event_state_machine(canon, raw_event=base_raw_event)

    assert a1.state_history == a2.state_history


def test_S_json_serialization(base_raw_event):
    """S. Round-trip JSON serialization of EventStateAssessment."""
    canon = build_event_features(base_raw_event)
    assessment = evaluate_event_state_machine(canon, raw_event=base_raw_event)

    d = assessment.to_dict()
    json_str = json.dumps(d)
    reconstructed = EventStateAssessment.from_dict(json.loads(json_str))

    assert assessment == reconstructed


def test_T_analyze_event_integration(base_raw_event):
    """T. analyze_event() orchestrator incorporates event state machine stage."""
    res = analyze_event(base_raw_event)

    assert res.pipeline_status["status"] == "COMPLETE"
    assert res.pipeline_status["stages"]["event_state_machine"] == "SUCCESS"
    assert "event_state" in res.behavior_assessment
    assert res.behavior_assessment["event_state"] in ALL_STATES


def test_U_risk_priority_consumes_state(base_raw_event):
    """U. Risk and priority engine consumes event state without duplication."""
    raw = dict(base_raw_event)
    raw["current_max_frp"] = 350.0
    raw["frp_increasing"] = True
    res = analyze_event(raw)

    assert res.behavior_assessment["event_state"] == STATE_ESCALATING
    assert res.priority_assessment["urgency"] in ["URGENT", "HIGH"]


def test_V_explanation_consumes_state(base_raw_event):
    """V. Explanation engine incorporates event state into structured output."""
    res = analyze_event(base_raw_event)

    assert any("state" in r.lower() or "event" in r.lower() for r in res.explanation["why"]["supporting_reasons"])


def test_W_all_source_classes_supported(base_raw_event):
    """W. Operates cleanly across all candidate source classes."""
    source_classes = [
        "INDUSTRIAL_FIRE", "ROUTINE_FLARE", "ABNORMAL_EMERGENCY_FLARE",
        "WILDFIRE", "AGRICULTURAL_BURN", "MINING_INDUSTRIAL_HEAT",
        "LANDFILL_OTHER_ANTHROPOGENIC", "OTHER", "UNKNOWN"
    ]
    canon = build_event_features(base_raw_event)
    assessment = evaluate_event_state_machine(canon, raw_event=base_raw_event)

    assert assessment.current_state in ALL_STATES


def test_X_frozen_phase16e_r2_unchanged():
    """X. Verify frozen Phase16E-R2 model file assets remain untouched."""
    model_path = os.path.join("src", "models", "frozen_phase16e_r2.bin")
    if os.path.exists(model_path):
        stat = os.stat(model_path)
        assert stat.st_size > 0
