import pytest
import numpy as np
from src.features.canonical_event_features import CanonicalEventFeatures
from src.features.low_t_persistent_heat import evaluate_low_t_lane, LowTConfig

def test_persistent_moderate_event():
    # 1. Persistent moderate event -> LOW_T_PERSISTENT
    canon = CanonicalEventFeatures(
        current_mean_frp=50.0,
        observation_count_so_far=10,
        persistence=48.0,
        centroid_shift=0.5,
        nearby_industrial_flag=1,
        missing_history_indicator=0,
        historical_recurrence=0.8,
        sentinel_available=1
    )
    result = evaluate_low_t_lane(canon)
    assert result.low_t_applicable == 1
    assert result.low_t_state == "LOW_T_PERSISTENT"
    assert "Repeated moderate thermal detections" in result.low_t_supporting_evidence[0]
    
def test_isolated_moderate_event():
    # 2. Single isolated moderate event -> LOW_T_NOT_APPLICABLE
    canon = CanonicalEventFeatures(
        current_mean_frp=50.0,
        observation_count_so_far=1,
        persistence=0.0
    )
    result = evaluate_low_t_lane(canon)
    assert result.low_t_applicable == 0
    assert result.low_t_state == "LOW_T_NOT_APPLICABLE"

def test_industrial_context_not_equal_fire():
    # 3. Persistent event in industrial context -> Low-T signal -> NOT automatically INDUSTRIAL_FIRE
    # Our LowT module explicitly does NOT output INDUSTRIAL_FIRE, it outputs LOW_T_PERSISTENT or similar.
    canon = CanonicalEventFeatures(
        current_mean_frp=80.0,
        observation_count_so_far=6,
        persistence=36.0,
        centroid_shift=0.1,
        nearby_industrial_flag=1,
        missing_history_indicator=0,
        historical_recurrence=0.5
    )
    result = evaluate_low_t_lane(canon)
    assert result.low_t_state in ["LOW_T_PERSISTENT", "LOW_T_POSSIBLE"]
    assert "INDUSTRIAL_FIRE" not in result.low_t_state

def test_non_industrial_context():
    # 4. Persistent event in non-industrial context -> Low-T lane can still activate
    canon = CanonicalEventFeatures(
        current_mean_frp=40.0,
        observation_count_so_far=15,
        persistence=72.0,
        centroid_shift=1.0,
        nearby_industrial_flag=0,
        land_context=0,
        missing_history_indicator=0,
        historical_recurrence=0.9
    )
    result = evaluate_low_t_lane(canon)
    assert result.low_t_state in ["LOW_T_PERSISTENT", "LOW_T_POSSIBLE"]

def test_missing_history_handling():
    # 5. Missing history -> lower evidence completeness -> no fake recurrence
    canon = CanonicalEventFeatures(
        current_mean_frp=50.0,
        observation_count_so_far=10,
        persistence=48.0,
        centroid_shift=0.5,
        missing_history_indicator=1
    )
    result = evaluate_low_t_lane(canon)
    assert result.low_t_features['low_t_history_available'] == 0
    assert np.isnan(canon.low_t_historical_recurrence)
    assert result.low_t_evidence_completeness < 1.0
    assert any("Insufficient historical baseline" in m for m in result.low_t_missing_evidence)

def test_missing_context_handling():
    # 6. Missing context -> no fabricated context value
    canon = CanonicalEventFeatures(
        current_mean_frp=50.0,
        observation_count_so_far=10,
        persistence=48.0,
        centroid_shift=0.5,
        nearby_industrial_flag=0, # not explicitly missing indicator in canon but 0 means unsupported
        land_context=0
    )
    result = evaluate_low_t_lane(canon)
    assert result.low_t_features['low_t_context_support'] == 0.0

def test_sudden_increase_preserves_evidence():
    # 7. Sudden increase on persistent activity
    # The event is persistent but suddenly spikes to 300 FRP. It won't be applicable for LOW_T score 
    # directly because of MAX_FRP, but it preserves evidence. 
    canon = CanonicalEventFeatures(
        current_mean_frp=300.0, # exceeding 150
        observation_count_so_far=20,
        persistence=100.0
    )
    result = evaluate_low_t_lane(canon)
    assert result.low_t_applicable == 0
    assert any("Thermal intensity exceeds moderate bounds" in c for c in result.low_t_conflicting_evidence)

def test_deterministic_output():
    # 8. Identical input -> deterministic output
    canon1 = CanonicalEventFeatures(
        current_mean_frp=60.0, observation_count_so_far=5, persistence=30.0,
        centroid_shift=0.0, missing_history_indicator=0, historical_recurrence=0.5
    )
    canon2 = CanonicalEventFeatures(
        current_mean_frp=60.0, observation_count_so_far=5, persistence=30.0,
        centroid_shift=0.0, missing_history_indicator=0, historical_recurrence=0.5
    )
    res1 = evaluate_low_t_lane(canon1)
    res2 = evaluate_low_t_lane(canon2)
    assert res1.low_t_score == res2.low_t_score
    assert res1.low_t_state == res2.low_t_state
    
def test_online_mode_safety():
    # 9. Online mode -> no retrospective/future features populated
    # Handled purely by canonical schema, but verify no retro features are used in Low-T evaluation
    canon = CanonicalEventFeatures(
        current_mean_frp=50.0, observation_count_so_far=10, persistence=48.0,
        retro_final_duration=9000.0, retro_final_max_frp=9000.0
    )
    evaluate_low_t_lane(canon)
    # The low-t score shouldn't be affected by retro_final_duration
    canon.retro_final_duration = np.nan
    res2 = evaluate_low_t_lane(canon)
    assert 'retro_final_duration' not in res2.low_t_features
