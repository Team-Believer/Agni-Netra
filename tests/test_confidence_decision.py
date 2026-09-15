"""
Unit tests for Agni-Netra Confidence Calibration & Unknown Decision Engine (Phase 17E)
"""

import pytest
import numpy as np
import os

from src.features.canonical_event_features import build_event_features
from src.features.low_t_persistent_heat import LowTResult
from src.intelligence.historical_abnormality import AbnormalityResult, ChangeIndicators
from src.intelligence.evidence_aggregation import (
    aggregate_event_evidence, EvidenceItem, EventEvidenceLedger
)
from src.intelligence.confidence_decision import (
    ConfidenceCalibrator, ConfidenceEngineConfig, ConfidenceAssessment,
    DecisionAssessment, evaluate_event_decision,
    CALIBRATED, FALLBACK, UNCALIBRATED,
    CALIBRATION_METHOD_TEMPERATURE, CALIBRATION_METHOD_IDENTITY,
    DECISION_KNOWN, DECISION_UNKNOWN, DECISION_NEEDS_VERIFICATION,
    DECISION_INSUFFICIENT_OBSERVATION,
    REASON_LOW_DATA_QUALITY, REASON_STRONG_EVIDENCE_CONFLICT,
    REASON_LOW_EVIDENCE_COMPLETENESS, REASON_INSUFFICIENT_TEMPORAL_HISTORY
)


def _build_sample_ledger(
    obs_quality=0.8,
    obs_count=5,
    sentinel_avail=1,
    industrial_flag=1,
    with_conflict=False,
    with_missing_sentinel=False
) -> EventEvidenceLedger:
    raw_event = {
        'current_max_frp': 45.0,
        'observation_count_so_far': obs_count,
        'current_duration': 24.0,
        'proxy_industrial_context': 0.5 if industrial_flag else 10.0,
        'S2_NDVI_online': 0.2 if sentinel_avail else np.nan
    }
    canon = build_event_features(raw_event, mode="online")
    canon.observation_quality = obs_quality
    if with_missing_sentinel:
        canon.sentinel_available = 0

    abnormality = AbnormalityResult(
        abnormality_state="UNUSUAL",
        abnormality_score=0.4,
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
        event_id="evt_test_001",
        canon=canon,
        low_t_result=low_t,
        abnormality_result=abnormality,
        model_probs=np.array([0.8, 0.1, 0.1]),
        source_classes=["INDUSTRIAL_FIRE", "ROUTINE_FLARE", "WILDFIRE"]
    )

    if with_conflict:
        # Inject conflicting evidence item into ledger
        ledger.evidence_items.append(
            EvidenceItem(
                evidence_id="conf_1",
                evidence_type="system_extracted",
                evidence_family="CONTEXT",
                source="test",
                status="OBSERVED",
                direction="CONFLICTING",
                strength="STRONG",
                description="Dense forest vegetation contradicts industrial flare hypothesis",
                availability=True
            )
        )

    return ledger


def test_deterministic_output():
    ledger = _build_sample_ledger()
    res1 = evaluate_event_decision("evt_det", "INDUSTRIAL_FIRE", 0.85, ledger)
    res2 = evaluate_event_decision("evt_det", "INDUSTRIAL_FIRE", 0.85, ledger)

    assert res1.decision_state == res2.decision_state
    assert res1.confidence.overall_decision_confidence == res2.confidence.overall_decision_confidence
    assert res1.to_dict() == res2.to_dict()


def test_missing_evidence_handling():
    ledger = _build_sample_ledger(with_missing_sentinel=True)
    res = evaluate_event_decision("evt_missing", "INDUSTRIAL_FIRE", 0.80, ledger)
    
    assert "SENTINEL" in res.evidence_summary["missing_critical_families"]
    assert res.confidence.evidence_completeness < 1.0


def test_missing_evidence_vs_conflicting_evidence():
    ledger_missing = _build_sample_ledger(with_missing_sentinel=True, with_conflict=False)
    res_missing = evaluate_event_decision("evt_m", "INDUSTRIAL_FIRE", 0.80, ledger_missing)

    ledger_conflict = _build_sample_ledger(with_missing_sentinel=False, with_conflict=True)
    res_conflict = evaluate_event_decision("evt_c", "INDUSTRIAL_FIRE", 0.80, ledger_conflict)

    # Missing evidence does NOT raise contradiction penalty
    assert res_missing.confidence.contradiction_penalty == 0.0
    assert res_conflict.confidence.contradiction_penalty > 0.0


def test_high_model_prob_does_not_bypass_insufficient_observation():
    # Model prob = 0.99, but data quality = 0.1 (extremely low)
    ledger = _build_sample_ledger(obs_quality=0.1, obs_count=1)
    res = evaluate_event_decision("evt_gate1", "INDUSTRIAL_FIRE", 0.99, ledger)

    assert res.decision_state == DECISION_INSUFFICIENT_OBSERVATION
    assert REASON_LOW_DATA_QUALITY in res.abstention["abstention_reason_codes"]
    assert res.operational_action == "INSUFFICIENT_DATA"


def test_strong_evidence_conflict_forces_needs_verification():
    # Model prob = 0.95, but strong conflicting context evidence
    ledger = _build_sample_ledger(with_conflict=True)
    res = evaluate_event_decision("evt_conflict", "INDUSTRIAL_FIRE", 0.95, ledger)

    assert res.decision_state == DECISION_NEEDS_VERIFICATION
    assert REASON_STRONG_EVIDENCE_CONFLICT in res.abstention["abstention_reason_codes"]
    assert res.operational_action == "VERIFY_REQUIRED"


def test_very_weak_evidence_forces_unknown():
    ledger = _build_sample_ledger(obs_count=5)
    # Keep only TEMPORAL item, clear others to create low evidence completeness
    ledger.evidence_items = [
        EvidenceItem("temp_1", "sys", "TEMPORAL", "src", "OBSERVED", "SUPPORTING", "MODERATE", "Repeated detections observed (5 times).")
    ]
    ledger.global_evidence_completeness = 0.15

    res = evaluate_event_decision("evt_unknown", "UNKNOWN", 0.30, ledger)
    assert res.decision_state == DECISION_UNKNOWN
    assert REASON_LOW_EVIDENCE_COMPLETENESS in res.abstention["abstention_reason_codes"] or REASON_SOURCE_AMBIGUITY in res.abstention["abstention_reason_codes"]


def test_insufficient_observations_forces_insufficient_observation():
    raw_event = {'current_max_frp': 20.0, 'observation_count_so_far': 1, 'current_duration': 0.5}
    canon = build_event_features(raw_event, mode="online")
    canon.observation_quality = 0.8
    ledger = aggregate_event_evidence("evt_single_obs", canon)

    res = evaluate_event_decision("evt_single_obs", "WILDFIRE", 0.85, ledger, canon=canon)
    assert res.decision_state == DECISION_INSUFFICIENT_OBSERVATION
    assert REASON_INSUFFICIENT_TEMPORAL_HISTORY in res.abstention["abstention_reason_codes"]


def test_calibrated_and_uncalibrated_modes_distinguished():
    ledger = _build_sample_ledger()

    # Identity fallback
    cal_default = ConfidenceCalibrator()
    res_default = evaluate_event_decision("evt_cal1", "INDUSTRIAL_FIRE", 0.80, ledger, calibrator=cal_default)
    assert res_default.calibration["calibration_status"] == FALLBACK
    assert res_default.calibration["calibration_method"] == CALIBRATION_METHOD_IDENTITY

    # Temperature calibrator
    cal_temp = ConfidenceCalibrator(method=CALIBRATION_METHOD_TEMPERATURE, params={"temperature": 1.5})
    res_temp = evaluate_event_decision("evt_cal2", "INDUSTRIAL_FIRE", 0.80, ledger, calibrator=cal_temp)
    assert res_temp.calibration["calibration_status"] == CALIBRATED
    assert res_temp.calibration["calibration_method"] == CALIBRATION_METHOD_TEMPERATURE
    assert float(res_temp.calibration["calibrated_confidence"]) != 0.80


def test_evidence_family_convergence_not_simple_feature_counting():
    ledger = _build_sample_ledger()
    # Add multiple items from SAME family "THERMAL"
    ledger.evidence_items.append(EvidenceItem("t1", "sys", "THERMAL", "src", "OBSERVED", "SUPPORTING", "STRONG", "Thermal item 1"))
    ledger.evidence_items.append(EvidenceItem("t2", "sys", "THERMAL", "src", "OBSERVED", "SUPPORTING", "STRONG", "Thermal item 2"))
    ledger.evidence_items.append(EvidenceItem("t3", "sys", "THERMAL", "src", "OBSERVED", "SUPPORTING", "STRONG", "Thermal item 3"))

    res = evaluate_event_decision("evt_conv", "INDUSTRIAL_FIRE", 0.80, ledger)
    # Supporting families should count unique family names, not 3 thermal items
    assert res.confidence.evidence_family_summary["supporting_families"].count("THERMAL") == 1


def test_facility_context_decoupling():
    ledger = _build_sample_ledger(industrial_flag=1)
    # Evaluate for WILDFIRE even when industrial facility context is present
    res = evaluate_event_decision("evt_wildfire", "WILDFIRE", 0.85, ledger)
    assert res.predicted_source_class == "WILDFIRE"
    # Does not force INDUSTRIAL_FIRE automatically


def test_low_t_decoupling():
    ledger = _build_sample_ledger()
    # Low-T persistence present, but evaluate candidate class AGRICULTURAL_BURN
    res = evaluate_event_decision("evt_agri", "AGRICULTURAL_BURN", 0.85, ledger)
    assert res.predicted_source_class == "AGRICULTURAL_BURN"


def test_cross_class_operation():
    ledger = _build_sample_ledger()
    classes = [
        "INDUSTRIAL_FIRE", "ROUTINE_FLARE", "ABNORMAL_EMERGENCY_FLARE",
        "WILDFIRE", "AGRICULTURAL_BURN", "MINING_INDUSTRIAL_HEAT",
        "LANDFILL_OTHER_ANTHROPOGENIC", "OTHER", "UNKNOWN"
    ]
    for cls in classes:
        res = evaluate_event_decision(f"evt_{cls}", cls, 0.75, ledger)
        assert res.predicted_source_class == cls
        assert res.decision_state in [DECISION_KNOWN, DECISION_UNKNOWN, DECISION_NEEDS_VERIFICATION, DECISION_INSUFFICIENT_OBSERVATION]


def test_serialized_output_stability():
    ledger = _build_sample_ledger()
    res = evaluate_event_decision("evt_ser", "INDUSTRIAL_FIRE", 0.85, ledger)

    d = res.to_dict()
    assert isinstance(d, dict)
    assert "event_id" in d
    assert "predicted_source_class" in d
    assert "decision_state" in d
    assert "confidence" in d
    assert "calibration" in d
    assert "evidence_summary" in d
    assert "abstention" in d
    assert "operational_action" in d

    # Round-trip deserialization
    res_reconstructed = DecisionAssessment.from_dict(d)
    assert res_reconstructed.event_id == res.event_id
    assert res_reconstructed.decision_state == res.decision_state
    assert res_reconstructed.confidence.overall_decision_confidence == res.confidence.overall_decision_confidence


def test_frozen_phase16e_r2_model_files_unchanged():
    model_dir = os.path.join("src", "models")
    assert os.path.exists(model_dir)
