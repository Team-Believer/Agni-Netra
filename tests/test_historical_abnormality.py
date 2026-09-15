import pytest
import numpy as np
from src.features.canonical_event_features import CanonicalEventFeatures
from src.intelligence.historical_abnormality import evaluate_abnormality

def test_normal_behavior_matching_baseline():
    # 1. Current behavior matching the historical baseline -> NORMAL
    canon = CanonicalEventFeatures(
        current_mean_frp=50.0,
        historical_mean_frp=48.0,
        missing_history_indicator=0,
        historical_event_frequency=5,
        recent_activity=5,
        footprint_change=1.0,
        change_point_indicator=0
    )
    res = evaluate_abnormality(canon)
    assert res.abnormality_state == "NORMAL"

def test_strong_frp_deviation():
    # 2. Strong FRP deviation -> elevated abnormality
    canon = CanonicalEventFeatures(
        current_mean_frp=300.0,
        historical_mean_frp=50.0,
        missing_history_indicator=0,
        historical_event_frequency=5,
        recent_activity=5,
        footprint_change=1.0,
        change_point_indicator=0
    )
    res = evaluate_abnormality(canon)
    assert res.abnormality_state in ["UNUSUAL", "HIGHLY_ABNORMAL"]
    assert res.deviation_components.frp_deviation > 0.5
    assert any("FRP unusually high" in s for s in res.supporting_evidence)

def test_strong_change_point_expansion():
    # 3. Strong change-point / footprint expansion -> elevated abnormality
    canon = CanonicalEventFeatures(
        current_mean_frp=60.0,
        historical_mean_frp=50.0,
        missing_history_indicator=0,
        historical_event_frequency=5,
        recent_activity=5,
        footprint_change=3.0, # large expansion
        change_point_indicator=1
    )
    res = evaluate_abnormality(canon)
    assert res.abnormality_state in ["UNUSUAL", "HIGHLY_ABNORMAL"]
    assert res.change_indicators.footprint_expansion == 1
    assert res.change_indicators.frp_spike == 1
    assert res.abnormality_score > 0.0

def test_missing_history_handling():
    # 4. Missing history -> UNKNOWN or explicitly limited abnormality
    canon = CanonicalEventFeatures(
        missing_history_indicator=1
    )
    res = evaluate_abnormality(canon)
    assert res.abnormality_state == "UNKNOWN"
    assert res.abnormality_score == 0.0
    assert res.history_support.history_available == 0
    assert any("Insufficient history" in m for m in res.missing_evidence)

def test_routine_flare_can_be_highly_abnormal():
    # 5. Routine flare can be HIGHLY_ABNORMAL if current behavior strongly deviates
    # (Source is just a concept here, we simulate it via very high baseline and even higher spike)
    canon = CanonicalEventFeatures(
        current_mean_frp=2000.0,
        historical_mean_frp=400.0,
        missing_history_indicator=0,
        historical_event_frequency=20,
        recent_activity=20,
        footprint_change=4.0,
        change_point_indicator=1
    )
    res = evaluate_abnormality(canon)
    assert res.abnormality_state == "HIGHLY_ABNORMAL"

def test_deterministic_output():
    # 7. Identical input gives deterministic output
    canon1 = CanonicalEventFeatures(
        current_mean_frp=60.0, historical_mean_frp=50.0, missing_history_indicator=0,
        historical_event_frequency=5, recent_activity=5, footprint_change=1.0, change_point_indicator=0
    )
    canon2 = CanonicalEventFeatures(
        current_mean_frp=60.0, historical_mean_frp=50.0, missing_history_indicator=0,
        historical_event_frequency=5, recent_activity=5, footprint_change=1.0, change_point_indicator=0
    )
    res1 = evaluate_abnormality(canon1)
    res2 = evaluate_abnormality(canon2)
    assert res1.abnormality_score == res2.abnormality_score
    assert res1.abnormality_state == res2.abnormality_state

def test_online_mode_safety():
    # 8. Online mode does not use future event observations
    # Tested structurally via CanonicalEventFeatures missing `retro_` prefix fields in computation
    canon = CanonicalEventFeatures(
        current_mean_frp=50.0, historical_mean_frp=48.0, missing_history_indicator=0,
        retro_final_duration=999.0
    )
    res = evaluate_abnormality(canon, mode="online")
    # Ensuring `retro_final_duration` doesn't alter duration_deviation
    assert res.deviation_components.duration_deviation == 0.0
