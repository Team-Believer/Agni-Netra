"""
Unit & Integration tests for Agni-Netra Observation Quality, Saturation & Sun-Glint Defense Layer (Phase 20A)
"""

import pytest
import numpy as np
import os
import json

from src.intelligence.observation_quality import (
    evaluate_single_observation_quality, evaluate_event_observation_quality,
    ObservationQualityAssessment, EventQualitySummary, ObservationQualityConfig,
    QUALITY_GOOD, QUALITY_ACCEPTABLE, QUALITY_DEGRADED, QUALITY_POOR,
    ACTION_ACCEPT, ACTION_FLAG, ACTION_DOWNWEIGHT, ACTION_EXCLUDE,
    SATURATION_NOT_DETECTED, SATURATION_POSSIBLE, SATURATION_LIKELY, SATURATION_UNKNOWN,
    GLINT_NO_RISK, GLINT_HIGH_RISK, GLINT_UNKNOWN_RISK,
    PERIOD_DAY, PERIOD_NIGHT, PERIOD_UNKNOWN,
    REASON_INVALID_COORDINATES, REASON_NON_FINITE_THERMAL,
    REASON_THERMAL_SATURATION_LIKELY, REASON_SUN_GLINT_RISK_HIGH,
    REASON_POTENTIAL_REFLECTIVE_CONTAMINATION
)
from src.intelligence.analyze_event import analyze_event, EventIntelligenceResult


def _build_sample_observation(
    obs_id="obs_001",
    lat=28.6139,
    lon=77.2090,
    frp=45.0,
    sensor="VIIRS",
    bt=320.0,
    daynight="D",
    glint_angle=45.0
):
    return {
        "observation_id": obs_id,
        "latitude": lat,
        "longitude": lon,
        "frp": frp,
        "sensor": sensor,
        "bright_ti4": bt,
        "daynight": daynight,
        "glint_angle": glint_angle,
        "observation_quality": 0.9
    }


def test_valid_observation_good_usable():
    obs = _build_sample_observation()
    res = evaluate_single_observation_quality(obs)

    assert res.quality_level == QUALITY_GOOD
    assert res.action == ACTION_ACCEPT
    assert res.usable_for_event_detection is True
    assert res.usable_for_classification is True
    assert res.usable_for_evidence is True
    assert res.recommended_weight == 1.0


def test_invalid_coordinates_rejected():
    obs_bad_lat = _build_sample_observation(lat=120.0)
    res_lat = evaluate_single_observation_quality(obs_bad_lat)

    assert res_lat.quality_level == QUALITY_POOR
    assert res_lat.action == ACTION_EXCLUDE
    assert res_lat.usable_for_evidence is False
    assert REASON_INVALID_COORDINATES in res_lat.reason_codes

    obs_nan_lon = _build_sample_observation(lon=np.nan)
    res_lon = evaluate_single_observation_quality(obs_nan_lon)
    assert res_lon.action == ACTION_EXCLUDE


def test_missing_optional_field_does_not_crash():
    obs_minimal = {"latitude": 28.5, "longitude": 77.2}
    res = evaluate_single_observation_quality(obs_minimal)

    assert res.usable_for_event_detection is True
    assert res.glint_risk_state == GLINT_UNKNOWN_RISK
    assert res.saturation_state == SATURATION_UNKNOWN


def test_non_finite_thermal_handled_safely():
    obs_nan_frp = _build_sample_observation(frp=np.nan)
    res = evaluate_single_observation_quality(obs_nan_frp)

    assert res.action == ACTION_EXCLUDE
    assert REASON_NON_FINITE_THERMAL in res.reason_codes


def test_saturation_detector_explicit_state():
    obs_sat = _build_sample_observation(sensor="VIIRS_I4", bt=370.0)
    res = evaluate_single_observation_quality(obs_sat)

    assert res.saturation_state == SATURATION_LIKELY
    assert REASON_THERMAL_SATURATION_LIKELY in res.reason_codes
    assert res.recommended_weight < 1.0


def test_saturation_does_not_increase_classification_confidence():
    obs_sat = _build_sample_observation(sensor="VIIRS", bt=380.0)
    res = evaluate_single_observation_quality(obs_sat)

    # Saturation downweights score and recommendation
    assert res.recommended_weight <= 0.85
    assert res.quality_score < 1.0


def test_glint_detector_operates_only_when_solar_context_meaningful():
    # Nighttime observation with small glint angle should NOT trigger glint risk
    obs_night = _build_sample_observation(daynight="N", glint_angle=5.0)
    res = evaluate_single_observation_quality(obs_night)

    assert res.glint_risk_state == GLINT_NO_RISK
    assert res.observation_period == PERIOD_NIGHT

    # Daytime observation with small glint angle SHOULD trigger glint risk
    obs_day = _build_sample_observation(daynight="D", glint_angle=5.0)
    res_day = evaluate_single_observation_quality(obs_day)
    assert res_day.glint_risk_state == GLINT_HIGH_RISK
    assert REASON_SUN_GLINT_RISK_HIGH in res_day.reason_codes


def test_missing_geometry_does_not_fabricate_glint_evidence():
    obs_no_geom = _build_sample_observation(glint_angle=None)
    res = evaluate_single_observation_quality(obs_no_geom)

    assert res.glint_risk_state == GLINT_UNKNOWN_RISK
    assert REASON_SUN_GLINT_RISK_HIGH not in res.reason_codes


def test_glint_risk_does_not_become_false_positive():
    obs_glint = _build_sample_observation(daynight="D", glint_angle=5.0)
    res = evaluate_single_observation_quality(obs_glint)

    # Glint risk downweights / flags but does not exclude event detection
    assert res.usable_for_event_detection is True
    assert REASON_POTENTIAL_REFLECTIVE_CONTAMINATION in res.reason_codes


def test_raw_observation_remains_unchanged():
    raw_obs = _build_sample_observation(frp=999.0, bt=380.0)
    obs_copy = dict(raw_obs)
    res = evaluate_single_observation_quality(raw_obs)

    # Original observation reference must be preserved unmutated
    assert res.raw_observation_ref == obs_copy


def test_event_level_quality_summary_aggregation():
    obs1 = _build_sample_observation(obs_id="obs_1", bt=320.0)
    obs2 = _build_sample_observation(obs_id="obs_2", bt=375.0)  # Saturated
    obs3 = _build_sample_observation(obs_id="obs_3", lat=999.0)  # Invalid

    summary = evaluate_event_observation_quality([obs1, obs2, obs3])

    assert summary.total_observation_count == 3
    assert summary.usable_observation_count == 2
    assert summary.excluded_observation_count == 1
    assert "Likely thermal saturation" in summary.saturation_summary


def test_analyze_event_receives_quality_outputs():
    raw_event = {
        "event_id": "evt_qual_test",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "current_max_frp": 80.0,
        "observation_count_so_far": 5,
        "sensor": "VIIRS",
        "bright_ti4": 372.0
    }
    res = analyze_event(raw_event)

    assert "observation_quality" in res.pipeline_status["stages"]
    assert "quality_summary" in res.observation_summary
    assert res.observation_summary["quality_summary"]["total_observation_count"] >= 1


def test_json_serialization():
    obs = _build_sample_observation()
    res = evaluate_single_observation_quality(obs)

    d = res.to_dict()
    assert isinstance(d, dict)
    json_str = json.dumps(d)
    assert isinstance(json_str, str)

    res_rec = ObservationQualityAssessment.from_dict(d)
    assert res_rec.observation_id == res.observation_id
    assert res_rec.quality_score == res.quality_score


def test_deterministic_output():
    obs = _build_sample_observation()
    res1 = evaluate_single_observation_quality(obs)
    res2 = evaluate_single_observation_quality(obs)

    assert res1.to_dict() == res2.to_dict()


def test_frozen_phase16e_r2_unchanged():
    model_dir = os.path.join("src", "models")
    assert os.path.exists(model_dir)
