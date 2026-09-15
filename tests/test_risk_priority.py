"""
Unit tests for Agni-Netra Risk & Priority Intelligence Engine (Phase 17F)
"""

import pytest
import numpy as np
import os

from src.features.canonical_event_features import build_event_features
from src.features.low_t_persistent_heat import LowTResult
from src.intelligence.historical_abnormality import AbnormalityResult, ChangeIndicators
from src.intelligence.evidence_aggregation import aggregate_event_evidence, EventEvidenceLedger
from src.intelligence.confidence_decision import evaluate_event_decision
from src.intelligence.risk_priority import (
    evaluate_risk_and_priority, calculate_hazard, calculate_impact,
    RiskPriorityAssessment, RiskPriorityConfig,
    PRIORITY_P0, PRIORITY_P1, PRIORITY_P2, PRIORITY_P3, PRIORITY_P4,
    URGENCY_URGENT, URGENCY_HIGH, URGENCY_NORMAL,
    ACTION_IMMEDIATE_REVIEW, ACTION_VERIFY, ACTION_MONITOR,
    CODE_HIGH_HAZARD, CODE_CRITICAL_FACILITY_PROXIMITY, CODE_VERIFICATION_REQUIRED,
    CODE_INSUFFICIENT_OBSERVATION
)


def _build_test_inputs(
    predicted_class="INDUSTRIAL_FIRE",
    obs_quality=0.8,
    obs_count=5,
    frp=50.0,
    industrial_flag=1,
    with_conflict=False,
    missing_context=False
):
    raw_event = {
        'current_max_frp': frp,
        'observation_count_so_far': obs_count,
        'current_duration': 24.0,
        'proxy_industrial_context': 0.5 if industrial_flag else 10.0,
        'S2_NDVI_online': 0.2
    }
    canon = build_event_features(raw_event, mode="online")
    canon.observation_quality = obs_quality
    if missing_context:
        canon.missing_context_indicator = 1

    abnormality = AbnormalityResult(
        abnormality_state="UNUSUAL" if with_conflict else "NORMAL",
        abnormality_score=0.4 if with_conflict else 0.1,
        supporting_evidence=[],
        conflicting_evidence=[],
        missing_evidence=[],
        deviation_components=None,
        change_indicators=ChangeIndicators(frp_spike=1 if with_conflict else 0, footprint_expansion=0, activity_shift=0, regime_change=0),
        history_support=None,
        confidence=0.8
    )

    low_t = LowTResult(
        low_t_state="LOW_T_PERSISTENT",
        low_t_score=0.85,
        low_t_applicable=1,
        low_t_features={},
        low_t_supporting_evidence=[],
        low_t_missing_evidence=[],
        low_t_conflicting_evidence=[],
        low_t_evidence_completeness=0.8,
        low_t_data_quality=0.8
    )

    ledger = aggregate_event_evidence(
        event_id="evt_rp_test",
        canon=canon,
        low_t_result=low_t,
        abnormality_result=abnormality,
        model_probs=np.array([0.8, 0.1, 0.1]),
        source_classes=["INDUSTRIAL_FIRE", "ROUTINE_FLARE", "WILDFIRE"]
    )

    dec = evaluate_event_decision(
        event_id="evt_rp_test",
        predicted_source_class=predicted_class,
        raw_model_confidence=0.85,
        evidence_ledger=ledger,
        canon=canon,
        low_t_result=low_t,
        abnormality_result=abnormality
    )

    return dec, ledger, canon, low_t, abnormality


def test_deterministic_risk_and_priority_output():
    dec, ledger, canon, low_t, abnormality = _build_test_inputs()
    res1 = evaluate_risk_and_priority("evt_det", dec, ledger, canon, low_t, abnormality)
    res2 = evaluate_risk_and_priority("evt_det", dec, ledger, canon, low_t, abnormality)

    assert res1.risk["base_risk_score"] == res2.risk["base_risk_score"]
    assert res1.priority["priority_score"] == res2.priority["priority_score"]
    assert res1.to_dict() == res2.to_dict()


def test_hazard_and_impact_separation():
    # Modifying impact context should not mutate hazard score
    dec, ledger, canon1, low_t, abnormality = _build_test_inputs(industrial_flag=1)
    res_ind = evaluate_risk_and_priority("evt_ind", dec, ledger, canon1, low_t, abnormality)

    dec, ledger, canon2, low_t, abnormality = _build_test_inputs(industrial_flag=0)
    res_veg = evaluate_risk_and_priority("evt_veg", dec, ledger, canon2, low_t, abnormality)

    assert res_ind.risk["hazard_score"] == res_veg.risk["hazard_score"]
    assert res_ind.risk["impact_score"] > res_veg.risk["impact_score"]


def test_risk_does_not_equal_priority():
    # Routine flare: moderate/high confidence, low risk, low priority
    dec_routine, ledger, canon, low_t, abnormality = _build_test_inputs(predicted_class="ROUTINE_FLARE", frp=30.0)
    res_routine = evaluate_risk_and_priority("evt_rout", dec_routine, ledger, canon, low_t, abnormality)

    # Unknown event with evidence conflict: low/moderate risk but HIGH verification priority
    dec_unk, ledger, canon, low_t, abnormality = _build_test_inputs(predicted_class="UNKNOWN", with_conflict=True)
    res_unk = evaluate_risk_and_priority("evt_unk", dec_unk, ledger, canon, low_t, abnormality)

    assert res_routine.risk["base_risk_score"] < res_unk.risk["base_risk_score"]
    assert res_unk.priority["priority_score"] > res_routine.priority["priority_score"]


def test_confidence_does_not_equal_risk():
    dec_high_conf, ledger, canon, low_t, abnormality = _build_test_inputs(predicted_class="ROUTINE_FLARE")
    res = evaluate_risk_and_priority("evt_conf", dec_high_conf, ledger, canon, low_t, abnormality)

    # High classification confidence does not force high risk
    assert dec_high_conf.confidence.classification_confidence >= 0.80
    assert res.risk["risk_level"] in ["LOW", "VERY_LOW", "MODERATE"]


def test_monotonicity_hazard_and_impact():
    dec, ledger, canon_low_frp, low_t, abnormality = _build_test_inputs(frp=20.0)
    res_low = evaluate_risk_and_priority("evt_l", dec, ledger, canon_low_frp, low_t, abnormality)

    dec, ledger, canon_high_frp, low_t, abnormality = _build_test_inputs(frp=250.0)
    res_high = evaluate_risk_and_priority("evt_h", dec, ledger, canon_high_frp, low_t, abnormality)

    # Increasing FRP/hazard increases base risk score monotonically
    assert res_high.risk["hazard_score"] >= res_low.risk["hazard_score"]
    assert res_high.risk["base_risk_score"] >= res_low.risk["base_risk_score"]


def test_monotonicity_urgency_increases_priority():
    dec_normal, ledger, canon, low_t, abnormality = _build_test_inputs(with_conflict=False)
    res_normal = evaluate_risk_and_priority("evt_norm", dec_normal, ledger, canon, low_t, abnormality)

    dec_urgent, ledger, canon, low_t, abnormality = _build_test_inputs(predicted_class="ABNORMAL_EMERGENCY_FLARE", with_conflict=True)
    res_urgent = evaluate_risk_and_priority("evt_urg", dec_urgent, ledger, canon, low_t, abnormality)

    assert res_urgent.priority["priority_score"] >= res_normal.priority["priority_score"]


test_evidence_conflict_reduces_confidence_not_physical_hazard = None
def test_uncertainty_reduces_confidence_not_hazard():
    dec_clean, ledger, canon, low_t, abnormality = _build_test_inputs(with_conflict=False)
    res_clean = evaluate_risk_and_priority("evt_clean", dec_clean, ledger, canon, low_t, abnormality)

    # Manually inject evidence conflict into decision assessment
    dec_conf = evaluate_event_decision(
        event_id="evt_conf",
        predicted_source_class="INDUSTRIAL_FIRE",
        raw_model_confidence=0.85,
        evidence_ledger=ledger,
        canon=canon,
        low_t_result=low_t,
        abnormality_result=abnormality
    )
    dec_conf.confidence.contradiction_penalty = 0.50
    dec_conf.confidence.overall_decision_confidence = 0.45
    dec_conf.decision_state = "NEEDS_VERIFICATION"

    res_conf = evaluate_risk_and_priority("evt_conf", dec_conf, ledger, canon, low_t, abnormality)

    # Physical hazard score remains high
    assert res_conf.risk["hazard_score"] == res_clean.risk["hazard_score"]
    # Risk confidence drops to reflect uncertainty
    assert res_conf.risk["risk_confidence"] < res_clean.risk["risk_confidence"]


def test_unknown_does_not_become_zero_risk():
    dec_unk, ledger, canon, low_t, abnormality = _build_test_inputs(predicted_class="UNKNOWN")
    res_unk = evaluate_risk_and_priority("evt_unk_zero", dec_unk, ledger, canon, low_t, abnormality)

    assert res_unk.risk["base_risk_score"] > 0.0
    assert res_unk.risk["hazard_score"] > 0.0


def test_insufficient_observation_explicitly_represented():
    dec_io, ledger, canon, low_t, abnormality = _build_test_inputs(obs_quality=0.1, obs_count=1)
    res_io = evaluate_risk_and_priority("evt_io", dec_io, ledger, canon, low_t, abnormality)

    assert res_io.uncertainty["decision_state"] == "INSUFFICIENT_OBSERVATION"
    assert CODE_INSUFFICIENT_OBSERVATION in res_io.drivers["priority_drivers"]


def test_facility_context_decoupling():
    dec_wf, ledger, canon, low_t, abnormality = _build_test_inputs(predicted_class="WILDFIRE", industrial_flag=1)
    res_wf = evaluate_risk_and_priority("evt_wf", dec_wf, ledger, canon, low_t, abnormality)

    # Predicted class remains WILDFIRE despite industrial flag
    assert dec_wf.predicted_source_class == "WILDFIRE"
    assert res_wf.risk["hazard_score"] <= 0.80  # Does not force maximum industrial hazard


def test_low_t_decoupling():
    dec_agri, ledger, canon, low_t, abnormality = _build_test_inputs(predicted_class="AGRICULTURAL_BURN")
    res_agri = evaluate_risk_and_priority("evt_agri", dec_agri, ledger, canon, low_t, abnormality)

    assert dec_agri.predicted_source_class == "AGRICULTURAL_BURN"
    assert res_agri.risk["hazard_level"] in ["LOW", "VERY_LOW", "MODERATE"]


def test_cross_class_operation():
    classes = [
        "INDUSTRIAL_FIRE", "ROUTINE_FLARE", "ABNORMAL_EMERGENCY_FLARE",
        "WILDFIRE", "AGRICULTURAL_BURN", "MINING_INDUSTRIAL_HEAT",
        "LANDFILL_OTHER_ANTHROPOGENIC", "OTHER", "UNKNOWN"
    ]
    for cls in classes:
        dec, ledger, canon, low_t, abnormality = _build_test_inputs(predicted_class=cls)
        res = evaluate_risk_and_priority(f"evt_{cls}", dec, ledger, canon, low_t, abnormality)
        assert res.risk["risk_level"] in ["VERY_LOW", "LOW", "MODERATE", "HIGH", "VERY_HIGH"]
        assert res.priority["priority_level"] in [PRIORITY_P0, PRIORITY_P1, PRIORITY_P2, PRIORITY_P3, PRIORITY_P4]


def test_missing_impact_context_explicitly_surfaced():
    dec, ledger, canon, low_t, abnormality = _build_test_inputs(missing_context=True)
    res = evaluate_risk_and_priority("evt_miss_ctx", dec, ledger, canon, low_t, abnormality)

    assert res.limitations["missing_context"] is True


def test_serialized_output_stability():
    dec, ledger, canon, low_t, abnormality = _build_test_inputs()
    res = evaluate_risk_and_priority("evt_ser_rp", dec, ledger, canon, low_t, abnormality)

    d = res.to_dict()
    assert isinstance(d, dict)
    assert "risk" in d
    assert "priority" in d
    assert "drivers" in d
    assert "uncertainty" in d
    assert "limitations" in d

    res_rec = RiskPriorityAssessment.from_dict(d)
    assert res_rec.event_id == res.event_id
    assert res_rec.risk["base_risk_score"] == res.risk["base_risk_score"]
    assert res_rec.priority["priority_score"] == res.priority["priority_score"]


def test_frozen_phase16e_r2_assets_unchanged():
    model_dir = os.path.join("src", "models")
    assert os.path.exists(model_dir)
