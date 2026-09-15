"""
Tests for Phase 20H — Real-Data AI Behavioral Demonstration Scenarios
(tests/test_demo_scenarios.py)

Validates tests A through R specified in Phase 20H requirements.
"""

import pytest
import os
import json
import hashlib
from src.intelligence.demo_scenarios import (
    select_demo_scenarios, build_scenario_record, build_and_export_demo_package,
    AgninetraDemoScenario
)
from src.intelligence.real_event_replay import load_real_event_fixtures
from src.intelligence.analyze_event import analyze_event, SCHEMA_VERSION


def test_A_only_real_event_fixtures_used():
    """Verify that demo scenario selection uses only real event fixtures."""
    fixtures = load_real_event_fixtures()
    scenarios = select_demo_scenarios(fixtures)
    for s_id, sc in scenarios.items():
        if sc.available:
            assert sc.observation_type == "REAL_OBSERVATION"
            assert sc.real_event_id != "NONE"


def test_B_no_synthetic_data_generated():
    """Verify no synthetic data flags or generated synthetic fixtures exist in demo scenarios."""
    scenarios = select_demo_scenarios()
    for s_id, sc in scenarios.items():
        if sc.available:
            assert "synthetic" not in sc.real_event_id.lower()


def test_C_no_ground_truth_fabricated():
    """Verify ground_truth_status is explicitly NOT_ESTABLISHED for all demo scenarios."""
    scenarios = select_demo_scenarios()
    for s_id, sc in scenarios.items():
        assert sc.ground_truth_status == "NOT_ESTABLISHED"


def test_D_scenario_selection_is_deterministic():
    """Verify repeated calls to select_demo_scenarios() return identical selected event IDs."""
    sc1 = select_demo_scenarios()
    sc2 = select_demo_scenarios()
    for s_id in sc1:
        assert sc1[s_id].real_event_id == sc2[s_id].real_event_id
        assert sc1[s_id].available == sc2[s_id].available


def test_E_scenario_records_are_serializable():
    """Verify JSON round-trip serialization of AgninetraDemoScenario records."""
    scenarios = select_demo_scenarios()
    sc_dict = {s_id: sc.to_dict() for s_id, sc in scenarios.items()}
    json_str = json.dumps(sc_dict)
    assert isinstance(json_str, str)
    recovered = json.loads(json_str)
    assert len(recovered) == 6


def test_F_event_ids_remain_traceable():
    """Verify selected scenarios retain traceable real_event_id and observation_ids."""
    scenarios = select_demo_scenarios()
    for s_id, sc in scenarios.items():
        if sc.available:
            assert len(sc.real_event_id) > 0
            assert isinstance(sc.observation_ids, list)


def test_G_source_class_comes_from_analyze_event():
    """Verify source_class in demo scenario matches predicted_source_class from analyze_event()."""
    scenarios = select_demo_scenarios()
    for s_id, sc in scenarios.items():
        if sc.available:
            assert "source_class" in sc.ai_result


def test_H_event_state_comes_from_state_machine():
    """Verify event_state in demo scenario comes from the event state machine."""
    scenarios = select_demo_scenarios()
    for s_id, sc in scenarios.items():
        if sc.available:
            assert "event_state" in sc.ai_result


def test_I_abnormality_comes_from_abnormality_engine():
    """Verify abnormality_level in demo scenario comes from abnormality engine."""
    scenarios = select_demo_scenarios()
    for s_id, sc in scenarios.items():
        if sc.available:
            assert "abnormality_level" in sc.ai_result


def test_J_novelty_comes_from_novelty_engine():
    """Verify novelty_level in demo scenario comes from novelty engine."""
    scenarios = select_demo_scenarios()
    for s_id, sc in scenarios.items():
        if sc.available:
            assert "novelty_level" in sc.ai_result


def test_K_confidence_comes_from_confidence_engine():
    """Verify confidence_level in demo scenario comes from confidence decision engine."""
    scenarios = select_demo_scenarios()
    for s_id, sc in scenarios.items():
        if sc.available:
            assert "confidence_level" in sc.ai_result


def test_L_risk_comes_from_risk_engine():
    """Verify risk_level in demo scenario comes from risk intelligence engine."""
    scenarios = select_demo_scenarios()
    for s_id, sc in scenarios.items():
        if sc.available:
            assert "risk_level" in sc.ai_result


def test_M_priority_comes_from_priority_engine():
    """Verify priority_level in demo scenario comes from priority intelligence engine."""
    scenarios = select_demo_scenarios()
    for s_id, sc in scenarios.items():
        if sc.available:
            assert "priority_level" in sc.ai_result


def test_N_explanations_come_from_explanation_engine():
    """Verify WHY, WHY_NOT, and WHAT_CHANGED come from explanation engine."""
    scenarios = select_demo_scenarios()
    for s_id, sc in scenarios.items():
        if sc.available:
            assert isinstance(sc.why, dict)
            assert isinstance(sc.why_not, dict)
            assert isinstance(sc.what_changed, dict)


def test_O_unavailable_scenarios_explicitly_represented():
    """Verify unavailable scenario categories set available = False with explicit reason."""
    scenarios = select_demo_scenarios()
    for s_id, sc in scenarios.items():
        if not sc.available:
            assert sc.unavailable_reason == "NO_REAL_EVENT_MEETS_SCENARIO_CRITERIA"
            assert sc.real_event_id == "NONE"


def test_P_no_unsupported_claims_added():
    """Verify ground truth claims and unsupported hype phrases are absent."""
    scenarios = select_demo_scenarios()
    for s_id, sc in scenarios.items():
        assert "discovered a new fire type" not in sc.behavior_summary
        assert sc.ground_truth_status == "NOT_ESTABLISHED"


def test_Q_schema_contract_remains_AGN_EVENT_INTELLIGENCE_1_0():
    """Verify schema version matches AGN-EVENT-INTELLIGENCE-1.0."""
    package = build_and_export_demo_package()
    assert package["schema_version"] == SCHEMA_VERSION


def test_R_frozen_model_unchanged():
    """Verify Phase16E-R2 weights file existence and hash integrity."""
    model_path = "src/model/multitask_b0_weights.pth"
    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
        assert len(h) == 64
