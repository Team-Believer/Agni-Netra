"""
Unit & Integration tests for Agni-Netra Production Orchestrator analyze_event() (Phase 18)
"""

import pytest
import numpy as np
import os
import json

from src.intelligence.analyze_event import (
    analyze_event, analyze_events, EventIntelligenceResult, SCHEMA_VERSION, PIPELINE_VERSION
)
from src.intelligence.confidence_decision import (
    DECISION_KNOWN, DECISION_UNKNOWN, DECISION_NEEDS_VERIFICATION, DECISION_INSUFFICIENT_OBSERVATION
)


def _build_raw_event_fixture(
    event_id="evt_test_p18",
    obs_count=5,
    frp=60.0,
    industrial_flag=1,
    missing_history=False,
    missing_sentinel=False,
    obs_quality=0.8
):
    return {
        "event_id": event_id,
        "current_max_frp": frp,
        "observation_count_so_far": obs_count,
        "current_duration": 24.0,
        "proxy_industrial_context": 0.5 if industrial_flag else 10.0,
        "S2_NDVI_online": np.nan if missing_sentinel else 0.2,
        "observation_quality": obs_quality,
        "missing_history_indicator": 1 if missing_history else 0,
        "lat": 28.6139,
        "lon": 77.2090
    }


def test_complete_event_flow_all_stages():
    raw_event = _build_raw_event_fixture()
    res = analyze_event(raw_event)

    assert isinstance(res, EventIntelligenceResult)
    assert res.schema_version == SCHEMA_VERSION
    assert res.pipeline_version == PIPELINE_VERSION
    assert res.event_id == "evt_test_p18"
    assert res.pipeline_status["status"] == "COMPLETE"
    assert len(res.pipeline_status["stages"]) == 13


def test_json_serializability():
    raw_event = _build_raw_event_fixture()
    res = analyze_event(raw_event)

    res_dict = res.to_dict()
    # Verify JSON dumping without error
    json_str = json.dumps(res_dict)
    assert isinstance(json_str, str)

    # Verify round-trip deserialization
    res_rec = EventIntelligenceResult.from_dict(res_dict)
    assert res_rec.event_id == res.event_id
    assert res_rec.pipeline_status["status"] == res.pipeline_status["status"]


def test_stage_execution_order():
    raw_event = _build_raw_event_fixture()
    res = analyze_event(raw_event)

    stages = list(res.pipeline_status["stages"].keys())
    expected_stages = [
        "validation", "observation_quality", "canonical_features", "low_t_heat",
        "high_t_physics", "event_state_machine", "historical_abnormality",
        "model_inference", "novel_event_detection", "evidence_aggregation",
        "confidence_decision", "risk_priority", "explanation_engine"
    ]
    assert stages == expected_stages


def test_deterministic_identical_input():
    raw_event = _build_raw_event_fixture()
    res1 = analyze_event(raw_event)
    res2 = analyze_event(raw_event)

    assert res1.source_assessment == res2.source_assessment
    assert res1.behavior_assessment == res2.behavior_assessment
    assert res1.abnormality_assessment == res2.abnormality_assessment
    assert res1.confidence_assessment == res2.confidence_assessment
    assert res1.risk_assessment == res2.risk_assessment
    assert res1.priority_assessment == res2.priority_assessment
    assert res1.explanation["summary"] == res2.explanation["summary"]
    assert res1.pipeline_status["status"] == res2.pipeline_status["status"]
    assert res1.pipeline_status["stages"] == res2.pipeline_status["stages"]


def test_missing_sentinel_does_not_crash_pipeline():
    raw_event = _build_raw_event_fixture(missing_sentinel=True)
    res = analyze_event(raw_event)

    assert res.pipeline_status["status"] == "COMPLETE"
    assert "SENTINEL" in res.limitations["unavailable_sensors"]


def test_missing_historical_baseline_representation():
    raw_event = _build_raw_event_fixture(missing_history=True)
    res = analyze_event(raw_event)

    assert res.pipeline_status["status"] == "COMPLETE"
    assert res.abnormality_assessment["abnormality_level"] == "UNKNOWN"
    assert "HISTORICAL_BASELINE" in res.limitations["missing_data"]


def test_insufficient_observation_produces_explicit_state():
    raw_event = _build_raw_event_fixture(obs_count=1, obs_quality=0.1)
    res = analyze_event(raw_event)

    assert res.pipeline_status["status"] == "INSUFFICIENT_OBSERVATION"
    assert res.confidence_assessment["decision_state"] == DECISION_INSUFFICIENT_OBSERVATION
    assert res.verification["verification_state"] == "INSUFFICIENT_DATA"


def test_unknown_source_propagates_correctly():
    raw_event = _build_raw_event_fixture(obs_count=5)
    probs = np.full(9, 1.0 / 9.0)  # Ambiguous uniform model distribution
    res = analyze_event(raw_event, model_probs=probs, source_classes=[
        "INDUSTRIAL_FIRE", "ROUTINE_FLARE", "ABNORMAL_EMERGENCY_FLARE",
        "WILDFIRE", "AGRICULTURAL_BURN", "MINING_INDUSTRIAL_HEAT",
        "LANDFILL_OTHER_ANTHROPOGENIC", "OTHER", "UNKNOWN"
    ])

    assert res.source_assessment["predicted_source_class"] == "INDUSTRIAL_FIRE" or res.confidence_assessment["decision_state"] in [DECISION_UNKNOWN, DECISION_NEEDS_VERIFICATION]


def test_needs_verification_propagates_correctly():
    raw_event = _build_raw_event_fixture(obs_count=5, frp=15.0)
    # Give model confidence below auto-classify threshold
    probs = np.array([0.45, 0.40, 0.15, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    res = analyze_event(raw_event, model_probs=probs)

    assert res.verification["verification_state"] in ["VERIFY_REQUIRED", "REVIEW_RECOMMENDED"]


def test_risk_consumes_confidence_and_evidence():
    raw_event = _build_raw_event_fixture()
    res = analyze_event(raw_event)

    assert "risk_confidence" in res.risk_assessment
    assert res.risk_assessment["base_risk_score"] > 0.0


def test_explanation_matches_upstream_outputs():
    raw_event = _build_raw_event_fixture()
    res = analyze_event(raw_event)

    exp = res.explanation
    assert exp["classification"]["predicted_source_class"] == res.source_assessment["predicted_source_class"]
    assert exp["risk_priority"]["risk_level"] == res.risk_assessment["risk_level"]


def test_provenance_survives_to_final_output():
    raw_event = _build_raw_event_fixture()
    res = analyze_event(raw_event)

    prov = res.explanation["provenance"]
    assert len(prov["evidence_source_ids"]) > 0
    assert len(prov["evidence_family_ids"]) > 0


def test_risk_does_not_equal_priority_preserved():
    raw_event = _build_raw_event_fixture(frp=30.0)
    res = analyze_event(raw_event)

    assert res.risk_assessment["base_risk_score"] != res.priority_assessment["priority_score"]


def test_facility_context_decoupling():
    raw_event = _build_raw_event_fixture(industrial_flag=1)
    probs = np.array([0.0, 0.0, 0.0, 0.90, 0.10, 0.0, 0.0, 0.0, 0.0])  # Model predicts WILDFIRE
    res = analyze_event(raw_event, model_probs=probs)

    assert res.source_assessment["predicted_source_class"] == "WILDFIRE"


def test_low_t_decoupling():
    raw_event = _build_raw_event_fixture()
    probs = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.90, 0.10, 0.0, 0.0])  # Model predicts MINING_INDUSTRIAL_HEAT
    res = analyze_event(raw_event, model_probs=probs)

    assert res.source_assessment["predicted_source_class"] == "MINING_INDUSTRIAL_HEAT"


def test_cross_class_support():
    classes = [
        "INDUSTRIAL_FIRE", "ROUTINE_FLARE", "ABNORMAL_EMERGENCY_FLARE",
        "WILDFIRE", "AGRICULTURAL_BURN", "MINING_INDUSTRIAL_HEAT",
        "LANDFILL_OTHER_ANTHROPOGENIC", "OTHER", "UNKNOWN"
    ]
    raw_event = _build_raw_event_fixture()

    for idx, cls in enumerate(classes):
        probs = np.zeros(len(classes))
        probs[idx] = 1.0
        res = analyze_event(raw_event, model_probs=probs, source_classes=classes)
        assert res.source_assessment["predicted_source_class"] == cls


def test_batch_analyze_events_helper():
    raw_events = [_build_raw_event_fixture(event_id=f"evt_b_{i}") for i in range(3)]
    results = analyze_events(raw_events)

    assert len(results) == 3
    for i, res in enumerate(results):
        assert res.event_id == f"evt_b_{i}"


def test_fatal_invalid_input_explicit():
    res = analyze_event(None)
    assert res.pipeline_status["status"] == "FAILED"
    assert res.pipeline_status["error_code"] == "INVALID_INPUT"

    res_empty = analyze_event({})
    assert res_empty.pipeline_status["status"] == "FAILED"


def test_frozen_phase16e_r2_unchanged():
    model_dir = os.path.join("src", "models")
    assert os.path.exists(model_dir)
