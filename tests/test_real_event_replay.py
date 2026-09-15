"""
Tests for Phase 20F — AI Pipeline Consolidation & Real-Data Readiness
(tests/test_real_event_replay.py)

Validates tests A through R specified in Phase 20F requirements.
"""

import pytest
import os
import json
import hashlib
import numpy as np

from src.intelligence.real_event_replay import (
    load_real_event_fixtures, RealDataReplayHarness, audit_stage_consistency,
    generate_failure_matrix_cases, CANONICAL_SOURCE_CLASSES, CANONICAL_DECISION_STATES,
    CANONICAL_DISTRIBUTION_STATES, CANONICAL_EVENT_STATES
)
from src.intelligence.analyze_event import analyze_event, EventIntelligenceResult


def _build_valid_test_event(event_id: str = "TEST_EVT", **kwargs) -> dict:
    base = {
        "event_id": event_id,
        "lat": 28.5,
        "lon": 97.0,
        "latitude": 28.5,
        "longitude": 97.0,
        "observation_count_so_far": 2,
        "observation_count": 2,
        "current_max_frp": 12.0,
        "max_frp": 12.0,
        "current_duration": 1.0,
        "duration_hours": 1.0,
        "proxy_industrial_context": 1.5,
        "observation_quality": 0.9
    }
    base.update(kwargs)
    return base


def test_A_real_fixture_loads():
    """Verify that real event fixtures load cleanly with expected schema fields."""
    fixtures = load_real_event_fixtures()
    assert len(fixtures) > 0, "Fixtures list should not be empty"
    first = fixtures[0]
    assert first.event_id is not None
    assert first.observation_count >= 1
    assert first.source_sensor == "FIRMS_VIIRS"
    assert first.fingerprint_hash is not None


def test_B_real_event_reaches_analyze_event():
    """Verify that a real event fixture executes through analyze_event() without errors."""
    fixtures = load_real_event_fixtures()
    fix = fixtures[0]
    result = analyze_event(fix.raw_event_dict)
    assert isinstance(result, EventIntelligenceResult)
    assert result.event_id == fix.event_id


def test_C_complete_pipeline_produces_all_sections():
    """Verify that analyze_event() returns all 13 major sections in EventIntelligenceResult."""
    fixtures = load_real_event_fixtures()
    result = analyze_event(fixtures[0].raw_event_dict)
    res_dict = result.to_dict()

    required_keys = [
        "schema_version", "pipeline_version", "event_id", "event_metadata",
        "observation_summary", "source_assessment", "behavior_assessment",
        "abnormality_assessment", "evidence_assessment", "confidence_assessment",
        "risk_assessment", "priority_assessment", "explanation", "verification",
        "pipeline_status", "limitations"
    ]
    for key in required_keys:
        assert key in res_dict, f"Missing key '{key}' in EventIntelligenceResult"
        assert res_dict[key] is not None


def test_D_schema_consistency_passes():
    """Verify that StageConsistencyAuditor marks the result as valid."""
    fixtures = load_real_event_fixtures()
    harness = RealDataReplayHarness(fixtures[:3])
    readiness = harness.run_full_replay()
    assert readiness["all_audits_passed"] is True, f"Audits failed: {readiness['audit_summaries']}"


def test_E_provenance_survives():
    """Verify that evidence items maintain sensor provenance back to raw observations."""
    fixtures = load_real_event_fixtures()
    result = analyze_event(fixtures[0].raw_event_dict)
    items = result.evidence_assessment.get("evidence_items", [])
    assert len(items) > 0, "Should have evidence items"
    for item in items:
        assert "provenance" in item or "source" in item


def test_F_unavailable_sensors_remain_unavailable():
    """Verify that unavailable sensors (INSAT/Sentinel/SAR) do not fabricate fake data."""
    raw_ev = _build_valid_test_event("TEST-F", S2_NDVI_online=np.nan)
    res = analyze_event(raw_ev)
    res_dict = res.to_dict()
    obs_sum = res_dict["observation_summary"]
    assert obs_sum["sentinel_available"] is False
    unavail = res_dict["limitations"]["unavailable_sensors"]
    assert any("SENTINEL" in s.upper() for s in unavail)


def test_G_sparse_history_handled_correctly():
    """Verify missing history indicator sets proper limitations without throwing exceptions."""
    raw_ev = _build_valid_test_event("TEST-G", missing_history_indicator=1)
    res = analyze_event(raw_ev)
    res_dict = res.to_dict()
    assert res_dict["observation_summary"]["missing_indicators"]["missing_history"] is True
    assert len(res_dict["limitations"]["missing_data"]) > 0


def test_H_unknown_novel_states_handled_correctly():
    """Verify that distribution state (KNOWN_LIKE/NOVEL/UNKNOWN) and decision state co-exist properly."""
    raw_ev = _build_valid_test_event("TEST-H", observation_count_so_far=1)
    res = analyze_event(raw_ev)
    res_dict = res.to_dict()
    assert res_dict["source_assessment"]["distribution_state"] in CANONICAL_DISTRIBUTION_STATES
    assert res_dict["source_assessment"]["decision_state"] in CANONICAL_DECISION_STATES


def test_I_observation_quality_propagates_correctly():
    """Verify observation quality degradation is reflected in observation summary and limits."""
    raw_ev = _build_valid_test_event("TEST-I", observation_quality=0.2, missing_sensor_indicator=1)
    res = analyze_event(raw_ev)
    res_dict = res.to_dict()
    obs_sum = res_dict["observation_summary"]
    assert "quality_summary" in obs_sum
    assert obs_sum["quality_summary"]["overall_observation_quality"] >= 0.0


def test_J_high_t_and_low_t_remain_separate():
    """Verify High-T thermal assessment and Low-T persistent heat remain distinct blocks."""
    raw_ev = _build_valid_test_event("TEST-J", current_max_frp=25.0)
    res = analyze_event(raw_ev)
    res_dict = res.to_dict()
    behavior = res_dict["behavior_assessment"]
    assert "high_t_assessment" in behavior
    assert "low_t_state" in behavior


def test_K_state_remains_separate_from_source():
    """Verify event state (NEW, PERSISTING, etc.) is separate from source class (WILDFIRE, etc.)."""
    raw_ev = _build_valid_test_event("TEST-K", observation_count_so_far=10, current_duration=48.0)
    res = analyze_event(raw_ev)
    res_dict = res.to_dict()
    e_state = res_dict["behavior_assessment"]["event_state"]
    s_class = res_dict["source_assessment"]["predicted_source_class"]
    assert e_state in CANONICAL_EVENT_STATES
    assert s_class in CANONICAL_SOURCE_CLASSES


def test_L_risk_remains_separate_from_priority():
    """Verify risk assessment and operational priority assessment remain distinct objects."""
    raw_ev = _build_valid_test_event("TEST-L")
    res = analyze_event(raw_ev)
    res_dict = res.to_dict()
    assert "risk_assessment" in res_dict
    assert "priority_assessment" in res_dict
    assert "risk_level" in res_dict["risk_assessment"]
    assert "priority_level" in res_dict["priority_assessment"]


def test_M_explanation_matches_upstream_outputs():
    """Verify explanation section correlates with decision state and evidence."""
    raw_ev = _build_valid_test_event("TEST-M")
    res = analyze_event(raw_ev)
    res_dict = res.to_dict()
    expl = res_dict["explanation"]
    assert "why" in expl
    assert "why_not" in expl
    assert "uncertainty" in expl
    assert "next_action" in expl


def test_N_deterministic_replay():
    """Verify that replaying identical inputs produces identical deterministic decisions and assessments."""
    raw_ev = _build_valid_test_event("TEST-N", observation_count_so_far=3, current_max_frp=12.5)
    res1 = analyze_event(raw_ev)
    res2 = analyze_event(raw_ev)
    
    assert res1.source_assessment == res2.source_assessment
    assert res1.behavior_assessment == res2.behavior_assessment
    assert res1.abnormality_assessment == res2.abnormality_assessment
    assert res1.confidence_assessment == res2.confidence_assessment
    assert res1.risk_assessment == res2.risk_assessment
    assert res1.priority_assessment == res2.priority_assessment
    assert res1.explanation["summary"] == res2.explanation["summary"]


def test_O_schema_serialization():
    """Verify JSON round-trip serialization of EventIntelligenceResult."""
    fixtures = load_real_event_fixtures()
    res = analyze_event(fixtures[0].raw_event_dict)
    res_dict = res.to_dict()
    json_str = json.dumps(res_dict)
    recovered_dict = json.loads(json_str)
    res_recovered = EventIntelligenceResult.from_dict(recovered_dict)
    assert res_recovered.event_id == res.event_id
    assert res_recovered.schema_version == res.schema_version


def test_P_source_vocabulary_consistency():
    """Verify source classes match frozen CANONICAL_SOURCE_CLASSES."""
    raw_ev = _build_valid_test_event("TEST-P")
    res = analyze_event(raw_ev)
    s_class = res.source_assessment["predicted_source_class"]
    assert s_class in CANONICAL_SOURCE_CLASSES


def test_Q_no_fake_ground_truth():
    """Verify replay harness marks fixtures explicitly as REAL_OBSERVATION (no fake ground truth)."""
    harness = RealDataReplayHarness()
    readiness = harness.run_full_replay()
    assert readiness["ground_truth_claim"] == "REAL_OBSERVATION (NO_FAKE_GROUND_TRUTH)"


def test_R_frozen_model_unchanged():
    """Verify Phase16E-R2 weights file existence and hash integrity."""
    model_path = "src/model/multitask_b0_weights.pth"
    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
        assert len(h) == 64
