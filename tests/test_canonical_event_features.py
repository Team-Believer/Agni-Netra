import pytest
import numpy as np
from src.features.canonical_event_features import build_event_features, CanonicalEventFeatures

def test_canonical_schema_generation():
    raw_event = {
        'current_max_frp': 50.5,
        'observation_count_so_far': 3,
        'current_duration': 24.0,
        'proxy_industrial_context': 1.5,
        'S2_NDVI_online': 0.6
    }
    
    features = build_event_features(raw_event, mode="online")
    assert features.schema_version == "AGN-FEATURES-1.1"
    assert features.current_max_frp == 50.5
    assert features.observation_count_so_far == 3
    assert features.distance_to_industrial_context == 1.5
    assert features.sentinel_available == 1
    assert features.missing_history_indicator == 1
    assert np.isnan(features.retro_final_duration)
    assert np.isnan(features.retro_final_max_frp)

def test_deterministic_output():
    raw_event = {
        'current_max_frp': 100.0,
        'observation_count_so_far': 10,
        'current_duration': 48.0,
        'proxy_industrial_context': 0.5,
        'hist_median_frp': 20.0
    }
    
    feat1 = build_event_features(raw_event, mode="online")
    feat2 = build_event_features(raw_event, mode="online")
    
    # Compare output dicts directly, treating nan equality
    d1 = feat1.to_dict()
    d2 = feat2.to_dict()
    
    for k, v1 in d1.items():
        v2 = d2[k]
        if isinstance(v1, float) and np.isnan(v1):
            assert np.isnan(v2)
        else:
            assert v1 == v2

def test_leakage_safety():
    raw_event = {
        'current_max_frp': 10.0,
        'final_duration': 200.0,
        'final_max_frp': 500.0
    }
    
    feat_online = build_event_features(raw_event, mode="online")
    assert np.isnan(feat_online.retro_final_duration)
    assert np.isnan(feat_online.retro_final_max_frp)
    
    feat_retro = build_event_features(raw_event, mode="retrospective")
    assert feat_retro.retro_final_duration == 200.0
    assert feat_retro.retro_final_max_frp == 500.0

def test_missingness_handling():
    raw_event_missing = {
        'current_max_frp': 10.0,
        'observation_count_so_far': 1
    }
    
    feat = build_event_features(raw_event_missing, mode="online")
    assert feat.missing_context_indicator == 1
    assert feat.missing_history_indicator == 1
    assert feat.sentinel_available == 0
    assert feat.evidence_completeness == 0.25
    assert np.isnan(feat.distance_to_industrial_context)
    assert np.isnan(feat.historical_frp_deviation)
    assert np.isnan(feat.observation_spacing) # due to count == 1
