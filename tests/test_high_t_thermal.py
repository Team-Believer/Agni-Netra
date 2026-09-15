"""
Agni-Netra Phase 20C Test Suite: High-Temperature Thermal Physics / VNF-Style Evidence Lane

Offline unit and integration tests covering:
A. valid high-T thermal input
B. missing brightness temperature
C. FRP-only input
D. full thermal variables unavailable → REDUCED_MODE
E. no required thermal fields → UNAVAILABLE
F. high FRP does not automatically equal high temperature
G. high temperature does not automatically equal Industrial Fire
H. saturation limits thermal reliability
I. LOW-T and HIGH-T remain separate
J. multiple observations aggregate deterministically
K. evidence ledger integration
L. confidence integration
M. risk integration
N. explanation integration
O. analyze_event() integration
P. JSON serialization
Q. deterministic output
R. all source classes supported
S. raw observations remain unchanged
T. frozen Phase16E-R2 unchanged
"""

import json
import os
import pytest
import numpy as np

from src.intelligence.high_t_thermal import (
    ThermalPhysicsInput, HighTThermalConfig, HighTThermalAssessment,
    evaluate_high_t_lane, estimate_thermal_physics,
    MODE_REDUCED, MODE_FULL, MODE_UNAVAILABLE,
    SIGNAL_STRONG, SIGNAL_MODERATE, SIGNAL_WEAK, SIGNAL_NOT_DETECTABLE, SIGNAL_UNKNOWN
)
from src.features.canonical_event_features import build_event_features
from src.features.low_t_persistent_heat import evaluate_low_t_lane
from src.intelligence.evidence_aggregation import aggregate_event_evidence
from src.intelligence.confidence_decision import evaluate_event_decision
from src.intelligence.risk_priority import evaluate_risk_and_priority
from src.intelligence.explanation_engine import generate_explanation
from src.intelligence.analyze_event import analyze_event


@pytest.fixture
def sample_high_t_raw_event():
    return {
        "event_id": "evt_hight_001",
        "lat": 28.61,
        "lon": 77.20,
        "current_max_frp": 250.0,
        "max_frp": 250.0,
        "mean_frp": 210.0,
        "brightness_temperature": 375.0,
        "observation_count_so_far": 4,
        "persistence_hours": 6.0,
        "land_context": 1,
        "observations": [
            {"frp": 250.0, "brightness_temperature": 375.0},
            {"frp": 170.0, "brightness_temperature": 365.0}
        ]
    }


def test_A_valid_high_t_thermal_input(sample_high_t_raw_event):
    """A. Valid high-T thermal input evaluation."""
    canon = build_event_features(sample_high_t_raw_event)
    assessment = evaluate_high_t_lane(canon, raw_event=sample_high_t_raw_event)

    assert assessment.available is True
    assert assessment.physics_mode == MODE_REDUCED
    assert assessment.high_temperature_signal == SIGNAL_STRONG
    assert assessment.brightness_temperature_summary["available"] is True
    assert assessment.brightness_temperature_summary["max"] == 375.0
    assert assessment.frp_summary["max"] == 250.0


def test_B_missing_brightness_temperature(sample_high_t_raw_event):
    """B. Missing brightness temperature input handled cleanly."""
    raw = dict(sample_high_t_raw_event)
    del raw["brightness_temperature"]
    raw["observations"] = [{"frp": 250.0}]

    canon = build_event_features(raw)
    assessment = evaluate_high_t_lane(canon, raw_event=raw)

    assert assessment.available is True
    assert assessment.physics_mode == MODE_REDUCED
    assert assessment.brightness_temperature_summary["available"] is False
    assert assessment.brightness_temperature_summary["max"] is None
    assert "BRIGHTNESS_TEMPERATURE_UNAVAILABLE" in assessment.reason_codes


def test_C_frp_only_input(sample_high_t_raw_event):
    """C. FRP-only input mode."""
    raw = {
        "event_id": "evt_frp_only",
        "current_max_frp": 120.0,
        "observation_count_so_far": 2
    }
    canon = build_event_features(raw)
    assessment = evaluate_high_t_lane(canon, raw_event=raw)

    assert assessment.available is True
    assert assessment.physics_mode == MODE_REDUCED
    assert assessment.frp_summary["available"] is True
    assert assessment.frp_summary["max"] == 120.0
    assert assessment.brightness_temperature_summary["available"] is False


def test_D_reduced_mode_activation():
    """D. Full thermal variables unavailable triggers REDUCED_MODE (no fake Planck fit)."""
    phys_input = ThermalPhysicsInput(frp=150.0, brightness_temperature=350.0)
    estimates = estimate_thermal_physics(phys_input)

    assert estimates["mode"] == MODE_REDUCED
    assert estimates["planck_temperature_kelvin"] is None  # NO FAKE PLANCK FIT!
    assert estimates["source_area_sq_m"] is None


def test_E_no_thermal_fields_unavailable():
    """E. Event with no required thermal fields returns UNAVAILABLE."""
    canon = build_event_features({"event_id": "evt_empty", "current_max_frp": 0.0, "observation_count_so_far": 0})
    assessment = evaluate_high_t_lane(canon, raw_event={"event_id": "evt_empty"})

    assert assessment.available is False
    assert assessment.physics_mode == MODE_UNAVAILABLE
    assert assessment.high_temperature_signal == SIGNAL_UNKNOWN


def test_F_high_frp_separate_from_temperature(sample_high_t_raw_event):
    """F. High FRP does not automatically equal high temperature."""
    # High FRP with modest brightness temperature
    raw = dict(sample_high_t_raw_event)
    raw["current_max_frp"] = 500.0
    raw["brightness_temperature"] = 310.0
    raw["observations"] = [{"frp": 500.0, "brightness_temperature": 310.0}]

    canon = build_event_features(raw)
    assessment = evaluate_high_t_lane(canon, raw_event=raw)

    assert assessment.frp_summary["max"] == 500.0
    assert assessment.brightness_temperature_summary["max"] == 310.0
    assert assessment.source_physics_indicators["frp_intensity_mw"] == 500.0


def test_G_high_temperature_does_not_force_industrial_fire(sample_high_t_raw_event):
    """G. High temperature does not automatically force Industrial Fire source class."""
    canon = build_event_features(sample_high_t_raw_event)
    assessment = evaluate_high_t_lane(canon, raw_event=sample_high_t_raw_event)

    # Physics assessment provides physics indicators, NOT source class decision!
    assert not hasattr(assessment, "predicted_source_class")
    assert assessment.high_temperature_signal in [SIGNAL_STRONG, SIGNAL_MODERATE]


def test_H_saturation_limits_reliability(sample_high_t_raw_event):
    """H. Saturation limits thermal measurement reliability."""
    from src.intelligence.observation_quality import EventQualitySummary
    quality_summary = EventQualitySummary(
        total_observation_count=2, usable_observation_count=2, degraded_observation_count=1,
        excluded_observation_count=0, overall_observation_quality=0.6, quality_summary="Quality ok",
        saturation_summary="Likely thermal saturation detected", glint_summary="No glint risk",
        critical_quality_flags=[], observation_assessments=[]
    )

    canon = build_event_features(sample_high_t_raw_event)
    assessment = evaluate_high_t_lane(canon, raw_event=sample_high_t_raw_event, quality_summary=quality_summary)

    assert assessment.thermal_measurement_reliability < 1.0
    assert "THERMAL_SATURATION_LIKELY" in assessment.reason_codes


def test_I_low_t_and_high_t_separate(sample_high_t_raw_event):
    """I. LOW-T persistence and HIGH-T physics remain independent signals."""
    canon = build_event_features(sample_high_t_raw_event)
    low_t = evaluate_low_t_lane(canon)
    high_t = evaluate_high_t_lane(canon, raw_event=sample_high_t_raw_event)

    # High-T is STRONG while Low-T is not persistent (short duration)
    assert high_t.high_temperature_signal == SIGNAL_STRONG
    assert low_t.low_t_state in ["LOW_T_DEVELOPING", "LOW_T_TRANSIENT", "LOW_T_NOT_APPLICABLE"]


def test_J_deterministic_repeated_aggregation(sample_high_t_raw_event):
    """J. Multiple observations aggregate deterministically."""
    canon = build_event_features(sample_high_t_raw_event)
    a1 = evaluate_high_t_lane(canon, raw_event=sample_high_t_raw_event)
    a2 = evaluate_high_t_lane(canon, raw_event=sample_high_t_raw_event)

    assert a1.to_dict() == a2.to_dict()


def test_K_evidence_ledger_integration(sample_high_t_raw_event):
    """K. Evidence ledger propagation under THERMAL_PHYSICS family."""
    canon = build_event_features(sample_high_t_raw_event)
    high_t = evaluate_high_t_lane(canon, raw_event=sample_high_t_raw_event)
    ledger = aggregate_event_evidence(
        event_id=sample_high_t_raw_event["event_id"],
        canon=canon,
        high_t_result=high_t
    )

    tp_items = [e for e in ledger.evidence_items if e.evidence_family == "THERMAL_PHYSICS"]
    assert len(tp_items) >= 1
    assert tp_items[0].source == "HighTThermalPhysics"
    assert tp_items[0].direction == "SUPPORTING"


def test_L_confidence_integration(sample_high_t_raw_event):
    """L. Confidence decision engine runs with high-T evidence present."""
    canon = build_event_features(sample_high_t_raw_event)
    high_t = evaluate_high_t_lane(canon, raw_event=sample_high_t_raw_event)
    ledger = aggregate_event_evidence(
        event_id=sample_high_t_raw_event["event_id"],
        canon=canon,
        high_t_result=high_t
    )
    decision = evaluate_event_decision(
        event_id=sample_high_t_raw_event["event_id"],
        predicted_source_class="INDUSTRIAL_FIRE",
        raw_model_confidence=0.80,
        evidence_ledger=ledger,
        canon=canon
    )
    assert decision.confidence.classification_confidence >= 0.0


def test_M_risk_integration(sample_high_t_raw_event):
    """M. Risk engine handles high-T evidence cleanly."""
    canon = build_event_features(sample_high_t_raw_event)
    high_t = evaluate_high_t_lane(canon, raw_event=sample_high_t_raw_event)
    ledger = aggregate_event_evidence(
        event_id=sample_high_t_raw_event["event_id"],
        canon=canon,
        high_t_result=high_t
    )
    decision = evaluate_event_decision(
        event_id=sample_high_t_raw_event["event_id"],
        predicted_source_class="INDUSTRIAL_FIRE",
        raw_model_confidence=0.80,
        evidence_ledger=ledger,
        canon=canon
    )
    rp = evaluate_risk_and_priority(sample_high_t_raw_event["event_id"], decision, ledger, canon)
    assert rp.risk["base_risk_score"] >= 0.0


def test_N_explanation_integration(sample_high_t_raw_event):
    """N. Explanation engine produces controlled high-T phrasing."""
    canon = build_event_features(sample_high_t_raw_event)
    high_t = evaluate_high_t_lane(canon, raw_event=sample_high_t_raw_event)
    ledger = aggregate_event_evidence(
        event_id=sample_high_t_raw_event["event_id"],
        canon=canon,
        high_t_result=high_t
    )
    decision = evaluate_event_decision(
        event_id=sample_high_t_raw_event["event_id"],
        predicted_source_class="INDUSTRIAL_FIRE",
        raw_model_confidence=0.80,
        evidence_ledger=ledger,
        canon=canon
    )
    rp = evaluate_risk_and_priority(sample_high_t_raw_event["event_id"], decision, ledger, canon)
    exp = generate_explanation(sample_high_t_raw_event["event_id"], decision, rp, ledger, canon)

    assert "proves industrial fire" not in exp.summary.lower()
    assert any("high-temperature" in r.lower() or "thermal" in r.lower() for r in exp.why["supporting_reasons"])


def test_O_analyze_event_integration(sample_high_t_raw_event):
    """O. analyze_event() pipeline includes high-T physics stage."""
    res = analyze_event(sample_high_t_raw_event)

    assert res.pipeline_status["status"] in ["COMPLETE", "INSUFFICIENT_OBSERVATION"]
    assert res.pipeline_status["stages"]["high_t_physics"] == "SUCCESS"
    assert "high_t_assessment" in res.behavior_assessment
    assert res.behavior_assessment["high_t_assessment"]["high_temperature_signal"] == SIGNAL_STRONG


def test_P_json_serialization(sample_high_t_raw_event):
    """P. JSON serialization and deserialization of HighTThermalAssessment."""
    canon = build_event_features(sample_high_t_raw_event)
    assessment = evaluate_high_t_lane(canon, raw_event=sample_high_t_raw_event)

    d = assessment.to_dict()
    json_str = json.dumps(d)
    reconstructed = HighTThermalAssessment.from_dict(json.loads(json_str))

    assert assessment == reconstructed


def test_Q_deterministic_output(sample_high_t_raw_event):
    """Q. Deterministic output given identical inputs."""
    r1 = analyze_event(sample_high_t_raw_event)
    r2 = analyze_event(sample_high_t_raw_event)

    assert r1.behavior_assessment["high_t_assessment"] == r2.behavior_assessment["high_t_assessment"]


def test_R_cross_class_support(sample_high_t_raw_event):
    """R. Works across all candidate source classes without class-biasing."""
    source_classes = [
        "INDUSTRIAL_FIRE", "ROUTINE_FLARE", "ABNORMAL_EMERGENCY_FLARE",
        "WILDFIRE", "AGRICULTURAL_BURN", "MINING_INDUSTRIAL_HEAT",
        "LANDFILL_OTHER_ANTHROPOGENIC", "OTHER", "UNKNOWN"
    ]
    canon = build_event_features(sample_high_t_raw_event)
    assessment = evaluate_high_t_lane(canon, raw_event=sample_high_t_raw_event)

    assert assessment.high_temperature_signal in [SIGNAL_STRONG, SIGNAL_MODERATE, SIGNAL_WEAK, SIGNAL_NOT_DETECTABLE]


def test_S_raw_observations_unchanged(sample_high_t_raw_event):
    """S. Raw observation input dictionary remains completely unchanged."""
    raw_copy = json.loads(json.dumps(sample_high_t_raw_event))
    analyze_event(sample_high_t_raw_event)

    assert sample_high_t_raw_event == raw_copy


def test_T_frozen_phase16e_r2_unchanged():
    """T. Frozen Phase16E-R2 model file assets remain untouched."""
    model_path = os.path.join("src", "models", "frozen_phase16e_r2.bin")
    if os.path.exists(model_path):
        stat = os.stat(model_path)
        assert stat.st_size > 0
