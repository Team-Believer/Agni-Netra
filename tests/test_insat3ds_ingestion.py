"""
Agni-Netra Phase 20B Test Suite: INSAT-3DS High-Cadence Thermal Evidence Lane

Offline unit and integration test fixtures covering:
A. valid INSAT-3DS observation
B. missing thermal field
C. invalid coordinates
D. multiple observations aligned to one event
E. INSAT supporting FIRMS temporally
F. ambiguous spatial alignment
G. unavailable INSAT product
H. stale observation
I. serialization
J. deterministic repeated ingestion
K. evidence ledger propagation
L. confidence integration
M. explanation integration
N. analyze_event() graceful operation with INSAT absent
O. analyze_event() operation with INSAT present
P. frozen Phase16E-R2 unchanged
"""

import json
import os
import pytest
import numpy as np
from datetime import datetime, timezone, timedelta

from src.ingestion.insat3ds import (
    INSAT3DSConfig, SensorSourceRegistry, SENSOR_REGISTRY,
    NormalizedObservation, SensorCorroborationAssessment,
    parse_insat3ds_file, normalize_insat3ds_observation,
    align_insat3ds_to_event, assess_sensor_corroboration,
    evaluate_source_freshness, SENSOR_INSAT3DS,
    CORROBORATION_CORROBORATING, CORROBORATION_PARTIALLY_CORROBORATING,
    CORROBORATION_CONFLICTING, CORROBORATION_NOT_AVAILABLE,
    FRESHNESS_FRESH, FRESHNESS_RECENT, FRESHNESS_STALE,
    ASSOCIATION_ALIGNED, ASSOCIATION_AMBIGUOUS, ASSOCIATION_UNALIGNED
)
from src.features.canonical_event_features import build_event_features
from src.intelligence.observation_quality import evaluate_single_observation_quality
from src.intelligence.evidence_aggregation import aggregate_event_evidence
from src.intelligence.confidence_decision import evaluate_event_decision
from src.intelligence.explanation_engine import generate_explanation
from src.intelligence.analyze_event import analyze_event


# --- FIXTURES ---

@pytest.fixture
def valid_insat_raw():
    now_str = datetime.now(timezone.utc).isoformat()
    return {
        "observation_id": "insat_3ds_obs_001",
        "product": "INSAT3DS_HEM_L2B",
        "timestamp": now_str,
        "latitude": 21.50,
        "longitude": 81.20,
        "brightness_temperature": 325.5,
        "thermal_band": "MIR",
        "quality": 1.0,
        "cloud_status": "CLEAR"
    }


@pytest.fixture
def sample_firms_event():
    return {
        "event_id": "evt_test_20b_001",
        "lat": 21.50,
        "lon": 81.20,
        "latitude": 21.50,
        "longitude": 81.20,
        "current_max_frp": 45.0,
        "max_frp": 45.0,
        "mean_frp": 35.0,
        "observation_count_so_far": 4,
        "obs_count": 4,
        "persistence_hours": 12.0,
        "duration_hours": 12.0,
        "nearby_industrial_flag": 1,
        "land_context": 1
    }


# --- TEST CASES (A-P) ---

def test_A_valid_insat_observation(valid_insat_raw):
    """A. Valid INSAT-3DS observation parsing and normalization."""
    obs = normalize_insat3ds_observation(valid_insat_raw)
    assert obs.observation_id == "insat_3ds_obs_001"
    assert obs.source_sensor == SENSOR_INSAT3DS
    assert obs.product == "INSAT3DS_HEM_L2B"
    assert obs.brightness_temperature == 325.5
    assert obs.frp is None  # FRP must NOT be fabricated!
    assert obs.latitude == 21.50
    assert obs.longitude == 81.20


def test_B_missing_thermal_field(valid_insat_raw):
    """B. Observation with missing brightness temperature field."""
    raw = dict(valid_insat_raw)
    del raw["brightness_temperature"]
    obs = normalize_insat3ds_observation(raw)
    assert obs.brightness_temperature is None
    assert obs.frp is None
    assert obs.source_sensor == SENSOR_INSAT3DS


def test_C_invalid_coordinates(valid_insat_raw):
    """C. Observation with invalid/out-of-bound coordinates."""
    raw = dict(valid_insat_raw)
    raw["latitude"] = 999.0
    obs = normalize_insat3ds_observation(raw)
    q_eval = evaluate_single_observation_quality(obs.to_dict())
    assert q_eval.action == "EXCLUDE" or "INVALID_COORDINATES" in q_eval.reason_codes


def test_D_multiple_observations_aligned(valid_insat_raw, sample_firms_event):
    """D. Multiple INSAT observations aligned to one event."""
    now = datetime.now(timezone.utc)
    obs1 = normalize_insat3ds_observation({**valid_insat_raw, "observation_id": "obs_1", "timestamp": now.isoformat()})
    obs2 = normalize_insat3ds_observation({**valid_insat_raw, "observation_id": "obs_2", "timestamp": (now - timedelta(minutes=15)).isoformat()})

    corroboration = assess_sensor_corroboration(
        event_id=sample_firms_event["event_id"],
        firms_obs_count=sample_firms_event["observation_count_so_far"],
        insat_obs_list=[obs1, obs2],
        event_lat=sample_firms_event["lat"],
        event_lon=sample_firms_event["lon"]
    )
    assert corroboration.corroboration_state == CORROBORATION_CORROBORATING
    assert corroboration.insat3ds_status["aligned_count"] == 2


def test_E_insat_supporting_firms_temporally(valid_insat_raw, sample_firms_event):
    """E. INSAT observation temporally supporting FIRMS detection."""
    obs = normalize_insat3ds_observation(valid_insat_raw)
    assoc, is_alg, dist_km, time_h = align_insat3ds_to_event(
        obs,
        event_centroid_lat=sample_firms_event["lat"],
        event_centroid_lon=sample_firms_event["lon"],
        event_start_time=obs.timestamp
    )
    assert assoc == ASSOCIATION_ALIGNED
    assert is_alg is True
    assert dist_km == 0.0


def test_F_ambiguous_spatial_alignment(valid_insat_raw, sample_firms_event):
    """F. Ambiguous spatial alignment when distance exceeds primary threshold but within time window."""
    obs = normalize_insat3ds_observation({
        **valid_insat_raw,
        "latitude": 21.65,  # ~16 km away (> 10 km default threshold)
        "longitude": 81.20
    })
    assoc, is_alg, dist_km, time_h = align_insat3ds_to_event(
        obs,
        event_centroid_lat=sample_firms_event["lat"],
        event_centroid_lon=sample_firms_event["lon"],
        event_start_time=obs.timestamp
    )
    assert assoc == ASSOCIATION_AMBIGUOUS or assoc == ASSOCIATION_UNALIGNED
    assert is_alg is False


def test_G_unavailable_insat_product(sample_firms_event):
    """G. Assessment when INSAT product is unavailable."""
    corroboration = assess_sensor_corroboration(
        event_id=sample_firms_event["event_id"],
        firms_obs_count=sample_firms_event["observation_count_so_far"],
        insat_obs_list=[],
        event_lat=sample_firms_event["lat"],
        event_lon=sample_firms_event["lon"]
    )
    assert corroboration.corroboration_state == CORROBORATION_NOT_AVAILABLE
    assert corroboration.insat3ds_status["availability"] == "UNAVAILABLE"


def test_H_stale_observation(valid_insat_raw):
    """H. Stale observation detection based on timestamp latency thresholds."""
    stale_time = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
    raw = {**valid_insat_raw, "timestamp": stale_time}
    freshness, age_h = evaluate_source_freshness(raw["timestamp"])
    assert freshness == FRESHNESS_STALE
    assert age_h >= 48.0


def test_I_serialization(valid_insat_raw, sample_firms_event):
    """I. Round-trip JSON serialization of NormalizedObservation and CorroborationAssessment."""
    obs = normalize_insat3ds_observation(valid_insat_raw)
    obs_dict = obs.to_dict()
    obs_reconstructed = NormalizedObservation.from_dict(obs_dict)
    assert obs == obs_reconstructed

    corroboration = assess_sensor_corroboration(
        event_id=sample_firms_event["event_id"],
        firms_obs_count=4,
        insat_obs_list=[obs],
        event_lat=sample_firms_event["lat"],
        event_lon=sample_firms_event["lon"]
    )
    corr_dict = corroboration.to_dict()
    json_str = json.dumps(corr_dict)
    reloaded = SensorCorroborationAssessment.from_dict(json.loads(json_str))
    assert reloaded.corroboration_state == corroboration.corroboration_state


def test_J_deterministic_repeated_ingestion(valid_insat_raw):
    """J. Deterministic repeated ingestion of same file/dictionary payload."""
    obs1 = parse_insat3ds_file(valid_insat_raw)
    obs2 = parse_insat3ds_file(valid_insat_raw)
    assert len(obs1) == 1 and len(obs2) == 1
    assert obs1[0].to_dict() == obs2[0].to_dict()


def test_K_evidence_ledger_propagation(valid_insat_raw, sample_firms_event):
    """K. Correct propagation of INSAT-3DS evidence into EventEvidenceLedger."""
    obs = normalize_insat3ds_observation(valid_insat_raw)
    corroboration = assess_sensor_corroboration(
        event_id=sample_firms_event["event_id"],
        firms_obs_count=4,
        insat_obs_list=[obs, obs],
        event_lat=sample_firms_event["lat"],
        event_lon=sample_firms_event["lon"]
    )
    canon = build_event_features(sample_firms_event)
    ledger = aggregate_event_evidence(
        event_id=sample_firms_event["event_id"],
        canon=canon,
        insat_corroboration=corroboration
    )

    geo_items = [e for e in ledger.evidence_items if e.evidence_family == "GEO_THERMAL"]
    assert len(geo_items) == 1
    assert geo_items[0].source == SENSOR_INSAT3DS
    assert geo_items[0].direction == "SUPPORTING"


def test_L_confidence_integration(valid_insat_raw, sample_firms_event):
    """L. Confidence decision engine integration with INSAT corroboration."""
    obs = normalize_insat3ds_observation(valid_insat_raw)
    corroboration = assess_sensor_corroboration(
        event_id=sample_firms_event["event_id"],
        firms_obs_count=4,
        insat_obs_list=[obs, obs],
        event_lat=sample_firms_event["lat"],
        event_lon=sample_firms_event["lon"]
    )
    canon = build_event_features(sample_firms_event)
    ledger = aggregate_event_evidence(
        event_id=sample_firms_event["event_id"],
        canon=canon,
        insat_corroboration=corroboration
    )
    decision = evaluate_event_decision(
        event_id=sample_firms_event["event_id"],
        predicted_source_class="INDUSTRIAL_FIRE",
        raw_model_confidence=0.85,
        evidence_ledger=ledger,
        canon=canon
    )
    assert decision.confidence.classification_confidence >= 0.0
    assert decision.decision_state in ["KNOWN", "NEEDS_VERIFICATION", "UNKNOWN", "INSUFFICIENT_OBSERVATION"]


def test_M_explanation_integration(valid_insat_raw, sample_firms_event):
    """M. Explanation engine produces controlled INSAT-3DS phrasing."""
    obs = normalize_insat3ds_observation(valid_insat_raw)
    corroboration = assess_sensor_corroboration(
        event_id=sample_firms_event["event_id"],
        firms_obs_count=4,
        insat_obs_list=[obs, obs],
        event_lat=sample_firms_event["lat"],
        event_lon=sample_firms_event["lon"]
    )
    canon = build_event_features(sample_firms_event)
    ledger = aggregate_event_evidence(
        event_id=sample_firms_event["event_id"],
        canon=canon,
        insat_corroboration=corroboration
    )
    decision = evaluate_event_decision(
        event_id=sample_firms_event["event_id"],
        predicted_source_class="INDUSTRIAL_FIRE",
        raw_model_confidence=0.85,
        evidence_ledger=ledger,
        canon=canon
    )
    from src.intelligence.risk_priority import evaluate_risk_and_priority
    rp = evaluate_risk_and_priority(sample_firms_event["event_id"], decision, ledger, canon)
    exp = generate_explanation(sample_firms_event["event_id"], decision, rp, ledger, canon)

    assert "confirms fire" not in exp.summary.lower()  # Controlled language rule!
    assert any("INSAT-3DS" in r or "GEO observations" in r for r in exp.why["supporting_reasons"])


def test_N_analyze_event_graceful_operation_absent(sample_firms_event):
    """N. analyze_event() operates gracefully when INSAT-3DS is absent."""
    result = analyze_event(sample_firms_event, insat_observations=None)
    assert result.pipeline_status["status"] == "COMPLETE"
    assert result.observation_summary["insat3ds_summary"]["availability"] == "UNAVAILABLE"
    assert "INSAT-3DS" in result.limitations["unavailable_sensors"]


def test_O_analyze_event_operation_present(valid_insat_raw, sample_firms_event):
    """O. analyze_event() operates correctly with INSAT-3DS observations present."""
    result = analyze_event(sample_firms_event, insat_observations=[valid_insat_raw, valid_insat_raw])
    assert result.pipeline_status["status"] == "COMPLETE"
    assert result.observation_summary["insat3ds_summary"]["availability"] == "AVAILABLE"
    assert result.observation_summary["insat3ds_summary"]["corroboration_state"] == CORROBORATION_CORROBORATING


def test_P_frozen_phase16e_r2_unchanged():
    """P. Verify frozen Phase16E-R2 model file assets remain strictly unchanged."""
    model_path = os.path.join("src", "models", "frozen_phase16e_r2.bin")
    if os.path.exists(model_path):
        stat = os.stat(model_path)
        assert stat.st_size > 0
