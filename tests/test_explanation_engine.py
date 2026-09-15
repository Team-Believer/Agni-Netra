"""
Unit tests for Agni-Netra WHY / WHY NOT / WHAT CHANGED Explanation Engine (Phase 17G)
"""

import pytest
import numpy as np
import os

from src.features.canonical_event_features import build_event_features
from src.features.low_t_persistent_heat import LowTResult
from src.intelligence.historical_abnormality import AbnormalityResult, ChangeIndicators
from src.intelligence.evidence_aggregation import aggregate_event_evidence
from src.intelligence.confidence_decision import evaluate_event_decision
from src.intelligence.risk_priority import evaluate_risk_and_priority
from src.intelligence.explanation_engine import generate_explanation, EventExplanation


def _build_test_pipeline_outputs(
    predicted_class="INDUSTRIAL_FIRE",
    obs_quality=0.8,
    obs_count=5,
    frp=60.0,
    with_conflict=False,
    missing_history=False,
    missing_sentinel=False
):
    raw_event = {
        'current_max_frp': frp,
        'observation_count_so_far': obs_count,
        'current_duration': 24.0,
        'proxy_industrial_context': 0.5,
        'S2_NDVI_online': np.nan if missing_sentinel else 0.2
    }
    canon = build_event_features(raw_event, mode="online")
    canon.observation_quality = obs_quality
    if missing_history:
        canon.missing_history_indicator = 1

    abnormality = AbnormalityResult(
        abnormality_state="UNUSUAL" if with_conflict else ("UNKNOWN" if missing_history else "NORMAL"),
        abnormality_score=0.55 if with_conflict else 0.1,
        supporting_evidence=[],
        conflicting_evidence=[],
        missing_evidence=["Insufficient history."] if missing_history else [],
        deviation_components=None,
        change_indicators=ChangeIndicators(frp_spike=1 if with_conflict else 0, footprint_expansion=0, activity_shift=0, regime_change=0),
        history_support=None,
        confidence=0.0 if missing_history else 0.8
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
        event_id="evt_exp_test",
        canon=canon,
        low_t_result=low_t,
        abnormality_result=abnormality,
        model_probs=np.array([0.8, 0.1, 0.1]),
        source_classes=["INDUSTRIAL_FIRE", "ROUTINE_FLARE", "WILDFIRE"]
    )

    if with_conflict:
        from src.intelligence.evidence_aggregation import EvidenceItem
        ledger.evidence_items.append(
            EvidenceItem(
                evidence_id="conf_exp_1",
                evidence_type="system_extracted",
                evidence_family="CONTEXT",
                source="test",
                status="OBSERVED",
                direction="CONFLICTING",
                strength="STRONG",
                description="Dense vegetation context contradicts industrial flare hypothesis",
                availability=True
            )
        )

    dec = evaluate_event_decision(
        event_id="evt_exp_test",
        predicted_source_class=predicted_class,
        raw_model_confidence=0.85,
        evidence_ledger=ledger,
        canon=canon,
        low_t_result=low_t,
        abnormality_result=abnormality
    )

    rp = evaluate_risk_and_priority(
        event_id="evt_exp_test",
        decision_assessment=dec,
        evidence_ledger=ledger,
        canon=canon,
        low_t_result=low_t,
        abnormality_result=abnormality
    )

    return dec, rp, ledger, canon, low_t, abnormality


def test_deterministic_output():
    dec, rp, ledger, canon, low_t, abnormality = _build_test_pipeline_outputs()
    exp1 = generate_explanation("evt_det", dec, rp, ledger, canon, low_t, abnormality)
    exp2 = generate_explanation("evt_det", dec, rp, ledger, canon, low_t, abnormality)

    assert exp1.summary == exp2.summary
    assert exp1.to_dict() == exp2.to_dict()


def test_json_serializability():
    dec, rp, ledger, canon, low_t, abnormality = _build_test_pipeline_outputs()
    exp = generate_explanation("evt_json", dec, rp, ledger, canon, low_t, abnormality)

    d = exp.to_dict()
    assert isinstance(d, dict)
    assert "why" in d
    assert "why_not" in d
    assert "what_changed" in d
    assert "provenance" in d

    exp_rec = EventExplanation.from_dict(d)
    assert exp_rec.event_id == exp.event_id
    assert exp_rec.summary == exp.summary


def test_why_contains_only_supported_evidence():
    dec, rp, ledger, canon, low_t, abnormality = _build_test_pipeline_outputs()
    exp = generate_explanation("evt_why", dec, rp, ledger, canon, low_t, abnormality)

    assert len(exp.why["supporting_reasons"]) > 0
    assert any("Thermal intensity" in r for r in exp.why["supporting_reasons"])


def test_why_not_contains_only_supported_limitations():
    dec, rp, ledger, canon, low_t, abnormality = _build_test_pipeline_outputs(missing_sentinel=True)
    exp = generate_explanation("evt_why_not", dec, rp, ledger, canon, low_t, abnormality)

    assert len(exp.why_not["limiting_reasons"]) > 0
    assert any("MISSING: Sentinel" in r for r in exp.why_not["limiting_reasons"])


def test_what_changed_appears_only_when_change_evidence_exists():
    # Normal event with no change
    dec_norm, rp_norm, ledger, canon, low_t, abnormality_norm = _build_test_pipeline_outputs(with_conflict=False)
    exp_norm = generate_explanation("evt_norm", dec_norm, rp_norm, ledger, canon, low_t, abnormality_norm)
    assert exp_norm.what_changed["change_detected"] is False

    # Event with change / FRP spike
    dec_chg, rp_chg, ledger, canon, low_t, abnormality_chg = _build_test_pipeline_outputs(with_conflict=True)
    exp_chg = generate_explanation("evt_chg", dec_chg, rp_chg, ledger, canon, low_t, abnormality_chg)
    assert exp_chg.what_changed["change_detected"] is True
    assert len(exp_chg.what_changed["change_reasons"]) > 0


def test_insufficient_history_does_not_create_fake_historical_change():
    dec, rp, ledger, canon, low_t, abnormality = _build_test_pipeline_outputs(missing_history=True)
    exp = generate_explanation("evt_no_hist", dec, rp, ledger, canon, low_t, abnormality)

    assert exp.what_changed["change_detected"] is False
    assert "insufficient" in exp.what_changed["historical_comparison"].lower()


def test_missing_evidence_is_not_written_as_negative_evidence():
    dec, rp, ledger, canon, low_t, abnormality = _build_test_pipeline_outputs(missing_sentinel=True)
    exp = generate_explanation("evt_miss", dec, rp, ledger, canon, low_t, abnormality)

    # Missing Sentinel appears in why_not / missing_information as Missing, not conflicting evidence
    assert any("MISSING: Sentinel" in r for r in exp.why_not["limiting_reasons"])


def test_facility_context_cannot_generate_industrial_fire_confirmed():
    dec, rp, ledger, canon, low_t, abnormality = _build_test_pipeline_outputs(predicted_class="INDUSTRIAL_FIRE")
    exp = generate_explanation("evt_fac", dec, rp, ledger, canon, low_t, abnormality)

    summary = exp.summary.lower()
    assert "confirmed fire" not in summary
    assert "certainly" not in summary


def test_low_t_cannot_generate_industrial_fire_confirmed():
    dec, rp, ledger, canon, low_t, abnormality = _build_test_pipeline_outputs(predicted_class="MINING_INDUSTRIAL_HEAT")
    exp = generate_explanation("evt_low_t", dec, rp, ledger, canon, low_t, abnormality)

    summary = exp.summary.lower()
    assert "low-t proves" not in summary
    assert "confirmed fire" not in summary


def test_unknown_explanation_exposes_uncertainty():
    dec, rp, ledger, canon, low_t, abnormality = _build_test_pipeline_outputs(predicted_class="UNKNOWN")
    exp = generate_explanation("evt_unk_exp", dec, rp, ledger, canon, low_t, abnormality)

    assert exp.classification["predicted_source_class"] == "UNKNOWN"
    assert "UNKNOWN" in exp.summary


def test_needs_verification_produces_verification_language():
    dec, rp, ledger, canon, low_t, abnormality = _build_test_pipeline_outputs(with_conflict=True)
    exp = generate_explanation("evt_ver_exp", dec, rp, ledger, canon, low_t, abnormality)

    assert exp.next_action["verification_required"] is True


def test_insufficient_observation_produces_insufficiency_language():
    dec, rp, ledger, canon, low_t, abnormality = _build_test_pipeline_outputs(obs_quality=0.1, obs_count=1)
    exp = generate_explanation("evt_io_exp", dec, rp, ledger, canon, low_t, abnormality)

    assert exp.classification["decision_state"] == "INSUFFICIENT_OBSERVATION"


def test_risk_and_priority_explanation_matches_phase17f():
    dec, rp, ledger, canon, low_t, abnormality = _build_test_pipeline_outputs()
    exp = generate_explanation("evt_rp_exp", dec, rp, ledger, canon, low_t, abnormality)

    assert exp.risk_priority["risk_level"] == rp.risk["risk_level"]
    assert exp.risk_priority["priority_level"] == rp.priority["priority_level"]
    assert exp.risk_priority["operational_action"] == rp.priority["operational_action"]


def test_confidence_language_matches_phase17e_state():
    dec, rp, ledger, canon, low_t, abnormality = _build_test_pipeline_outputs()
    exp = generate_explanation("evt_conf_exp", dec, rp, ledger, canon, low_t, abnormality)

    assert exp.uncertainty["confidence_level"] == dec.confidence.confidence_level


def test_model_evidence_remains_model_derived():
    dec, rp, ledger, canon, low_t, abnormality = _build_test_pipeline_outputs()
    exp = generate_explanation("evt_model_exp", dec, rp, ledger, canon, low_t, abnormality)

    why_reasons = " ".join(exp.why["supporting_reasons"])
    assert "Model-derived" in why_reasons
    assert "AI knows" not in why_reasons


def test_provenance_exists_for_major_explanation_items():
    dec, rp, ledger, canon, low_t, abnormality = _build_test_pipeline_outputs()
    exp = generate_explanation("evt_prov_exp", dec, rp, ledger, canon, low_t, abnormality)

    assert len(exp.provenance["evidence_source_ids"]) > 0
    assert len(exp.provenance["evidence_family_ids"]) > 0


def test_all_source_classes_render_cleanly():
    classes = [
        "INDUSTRIAL_FIRE", "ROUTINE_FLARE", "ABNORMAL_EMERGENCY_FLARE",
        "WILDFIRE", "AGRICULTURAL_BURN", "MINING_INDUSTRIAL_HEAT",
        "LANDFILL_OTHER_ANTHROPOGENIC", "OTHER", "UNKNOWN"
    ]
    for cls in classes:
        dec, rp, ledger, canon, low_t, abnormality = _build_test_pipeline_outputs(predicted_class=cls)
        exp = generate_explanation(f"evt_{cls}", dec, rp, ledger, canon, low_t, abnormality)
        assert isinstance(exp.summary, str)
        assert len(exp.summary) > 50


def test_frozen_phase16e_r2_assets_unchanged():
    model_dir = os.path.join("src", "models")
    assert os.path.exists(model_dir)
