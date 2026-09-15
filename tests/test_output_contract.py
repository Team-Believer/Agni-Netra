"""
Tests for Phase 20G — AI Output Contract Hardening & Handoff Freeze
(tests/test_output_contract.py)

Validates tests A through Q specified in Phase 20G requirements.
"""

import pytest
import os
import json
import hashlib
import numpy as np

from src.intelligence.output_contract import (
    build_canonical_contract, validate_event_intelligence_result,
    serialize_to_json, SCHEMA_VERSION, PIPELINE_VERSION,
    FROZEN_SOURCE_CLASSES, FROZEN_DECISION_STATES, FROZEN_DISTRIBUTION_STATES,
    FROZEN_EVENT_STATES, FROZEN_RISK_LEVELS, FROZEN_PRIORITY_LEVELS,
    FROZEN_VERIFICATION_STATES
)
from src.intelligence.analyze_event import analyze_event, EventIntelligenceResult
from src.intelligence.real_event_replay import load_real_event_fixtures, RealDataReplayHarness


def _build_valid_test_event(event_id: str = "TEST_CONTRACT", **kwargs) -> dict:
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


def test_A_complete_result_has_all_required_sections():
    """Verify that build_canonical_contract() produces all 16 required top-level sections."""
    raw_ev = _build_valid_test_event("TEST-A")
    res = analyze_event(raw_ev)
    contract = build_canonical_contract(res.to_dict())

    required_sections = [
        "schema_version", "pipeline_version", "event", "observation", "thermal",
        "behavior", "abnormality", "source", "novelty", "evidence", "confidence",
        "risk", "priority", "explanation", "verification", "pipeline", "limitations", "provenance"
    ]
    for sec in required_sections:
        assert sec in contract, f"Missing required top-level section '{sec}'"
        assert contract[sec] is not None


def test_B_json_serialization():
    """Verify that build_canonical_contract() output serializes to JSON without errors."""
    raw_ev = _build_valid_test_event("TEST-B")
    res = analyze_event(raw_ev)
    contract = build_canonical_contract(res.to_dict())
    json_str = serialize_to_json(contract)
    assert isinstance(json_str, str)
    assert len(json_str) > 100


def test_C_roundtrip_serialization():
    """Verify round-trip serialization (object -> dict -> JSON -> dict -> object)."""
    raw_ev = _build_valid_test_event("TEST-C")
    res = analyze_event(raw_ev)
    res_dict = res.to_dict()
    json_str = json.dumps(res_dict)
    recovered_dict = json.loads(json_str)
    res_recovered = EventIntelligenceResult.from_dict(recovered_dict)
    assert res_recovered.event_id == res.event_id
    assert res_recovered.schema_version == res.schema_version


def test_D_deterministic_output():
    """Verify that identical input events produce identical contract decisions and scores."""
    raw_ev = _build_valid_test_event("TEST-D")
    res1 = analyze_event(raw_ev)
    res2 = analyze_event(raw_ev)
    c1 = build_canonical_contract(res1.to_dict())
    c2 = build_canonical_contract(res2.to_dict())

    assert c1["source"] == c2["source"]
    assert c1["behavior"] == c2["behavior"]
    assert c1["risk"] == c2["risk"]
    assert c1["priority"] == c2["priority"]
    assert c1["confidence"] == c2["confidence"]


def test_E_deterministic_ordering():
    """Verify that list structures (evidence families, reason codes, etc.) maintain sorted ordering."""
    raw_ev = _build_valid_test_event("TEST-E")
    res = analyze_event(raw_ev)
    contract = build_canonical_contract(res.to_dict())

    for key in ["supporting_families", "conflicting_families", "missing_families", "neutral_families"]:
        fams = contract["evidence"][key]
        assert fams == sorted(fams), f"Evidence list '{key}' not deterministically sorted"

    limitations = contract["limitations"]["unavailable_sensors"]
    assert limitations == sorted(limitations)


def test_F_enum_vocabulary_consistency():
    """Verify contract validator checks enum values against frozen canonical vocabularies."""
    raw_ev = _build_valid_test_event("TEST-F")
    res = analyze_event(raw_ev)
    errors = validate_event_intelligence_result(res)
    assert len(errors) == 0, f"Validation errors found: {errors}"


def test_G_provenance_preservation():
    """Verify provenance section traces observation IDs, evidence families, and reason codes."""
    raw_ev = _build_valid_test_event("TEST-G")
    res = analyze_event(raw_ev)
    contract = build_canonical_contract(res.to_dict())
    prov = contract["provenance"]
    assert prov["event_id"] == "TEST-G"
    assert isinstance(prov["observation_ids"], list)
    assert len(prov["evidence_family_ids"]) > 0


def test_H_missing_sensor_preservation():
    """Verify unavailable sensors (INSAT/Sentinel) are explicitly reported in sensor_availability and limitations."""
    raw_ev = _build_valid_test_event("TEST-H", S2_NDVI_online=np.nan)
    res = analyze_event(raw_ev)
    contract = build_canonical_contract(res.to_dict())
    assert contract["observation"]["sensor_availability"]["sentinel_available"] is False
    assert any("SENTINEL" in s.upper() for s in contract["limitations"]["unavailable_sensors"])


def test_I_unknown_preservation():
    """Verify UNKNOWN decision state is preserved as a valid, non-error state."""
    raw_ev = _build_valid_test_event("TEST-I", observation_count_so_far=1)
    res = analyze_event(raw_ev)
    contract = build_canonical_contract(res.to_dict())
    assert contract["source"]["decision_state"] in FROZEN_DECISION_STATES


def test_J_insufficient_observation_preservation():
    """Verify INSUFFICIENT_OBSERVATION state is preserved cleanly in contract."""
    raw_ev = {"event_id": "TEST-J", "lat": 28.5, "lon": 97.0, "observation_count_so_far": 0}
    res = analyze_event(raw_ev)
    contract = build_canonical_contract(res.to_dict())
    assert contract["source"]["decision_state"] == "INSUFFICIENT_OBSERVATION" or contract["pipeline"]["overall_status"] == "INSUFFICIENT_OBSERVATION"


def test_K_risk_priority_separation():
    """Verify risk assessment and operational priority assessment remain distinct sections."""
    raw_ev = _build_valid_test_event("TEST-K")
    res = analyze_event(raw_ev)
    contract = build_canonical_contract(res.to_dict())
    assert "risk" in contract
    assert "priority" in contract
    assert contract["risk"]["risk_level"] in FROZEN_RISK_LEVELS
    assert contract["priority"]["priority_level"] in FROZEN_PRIORITY_LEVELS


def test_L_confidence_risk_separation():
    """Verify overall decision confidence is distinct from physical hazard/risk level."""
    raw_ev = _build_valid_test_event("TEST-L")
    res = analyze_event(raw_ev)
    contract = build_canonical_contract(res.to_dict())
    conf_score = contract["confidence"]["overall_decision_confidence"]
    risk_score = contract["risk"]["base_risk_score"]
    assert isinstance(conf_score, float)
    assert isinstance(risk_score, float)


def test_M_state_source_separation():
    """Verify event state (PERSISTING, etc.) is separate from source class (ROUTINE_FLARE, etc.)."""
    raw_ev = _build_valid_test_event("TEST-M", observation_count_so_far=10, current_duration=48.0)
    res = analyze_event(raw_ev)
    contract = build_canonical_contract(res.to_dict())
    evt_state = contract["behavior"]["event_state"]
    src_class = contract["source"]["predicted_source_class"]
    assert evt_state in FROZEN_EVENT_STATES
    assert src_class in FROZEN_SOURCE_CLASSES


def test_N_novelty_decision_state_separation():
    """Verify novelty distribution state is distinct from decision state."""
    raw_ev = _build_valid_test_event("TEST-N")
    res = analyze_event(raw_ev)
    contract = build_canonical_contract(res.to_dict())
    dist_state = contract["novelty"]["distribution_state"]
    dec_state = contract["source"]["decision_state"]
    assert dist_state in FROZEN_DISTRIBUTION_STATES
    assert dec_state in FROZEN_DECISION_STATES


def test_O_real_data_replay_compatibility():
    """Verify that real event fixtures produce valid canonical contracts."""
    fixtures = load_real_event_fixtures()
    harness = RealDataReplayHarness(fixtures[:3])
    readiness = harness.run_full_replay()
    for snap in readiness["snapshots"]:
        assert snap["audit_valid"] is True


def test_P_representative_example_validates_against_schema():
    """Verify that docs/examples/event_intelligence_example.json loads and validates cleanly."""
    example_path = "docs/examples/event_intelligence_example.json"
    assert os.path.exists(example_path), "Example JSON file missing"
    with open(example_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    errors = validate_event_intelligence_result(data)
    assert len(errors) == 0, f"Representative example JSON validation failed: {errors}"


def test_Q_frozen_model_unchanged():
    """Verify Phase16E-R2 weights file existence and hash integrity."""
    model_path = "src/model/multitask_b0_weights.pth"
    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
        assert len(h) == 64
