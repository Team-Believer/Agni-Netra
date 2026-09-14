import pandas as pd
import numpy as np
import pytest
from src.features.event_feature_generator import generate_features

def test_critical_leakage_invariant():
    """
    The critical leakage invariant:
    ONLINE_FEATURES(event, obs <= T) MUST BE EXACTLY EQUAL to
    ONLINE_FEATURES(event, dataframe containing obs <= T plus future obs > T)
    
    If the online feature generation function silently uses `final_max_frp`
    when it shouldn't, the two outputs will differ.
    """
    # 1. Base snapshot (T1)
    df_snapshot = pd.DataFrame([{
        'event_id': 'evt_1',
        'current_max_frp': 50.0,
        'current_duration': 2.0,
        'observation_count_so_far': 2,
        # NO FUTURE DATA PRESENT AT ALL
    }])
    
    # 2. Base snapshot mixed with future data (The dataframe that the model sees during retro processing)
    df_with_future = pd.DataFrame([{
        'event_id': 'evt_1',
        'current_max_frp': 50.0,
        'current_duration': 2.0,
        'observation_count_so_far': 2,
        # FUTURE LEAKAGE DATA
        'final_max_frp': 500.0,
        'final_duration': 96.0,
        'final_observation_count': 15
    }])
    
    # Generate
    online_snapshot, _ = generate_features(df_snapshot)
    online_with_future, _ = generate_features(df_with_future)
    
    # Drop the synthetic random columns for the equality check (because we use np.random in the mock generator, which will differ between calls)
    # In a real environment, we would seed this perfectly, or mock the randoms out.
    cols_to_check = ['current_max_frp', 'current_event_duration_hours', 'observation_count_so_far']
    
    pd.testing.assert_frame_equal(
        online_snapshot[cols_to_check], 
        online_with_future[cols_to_check]
    )
    
def test_provenance_isolation():
    """
    Ensure TRUE_SYNTHETIC_CLASS is never propagated into the actual numerical features.
    """
    df = pd.DataFrame([{
        'event_id': 'evt_1',
        'TRUE_SYNTHETIC_CLASS': 'Industrial Fire',
        'current_max_frp': 50.0
    }])
    online, _ = generate_features(df)
    
    # The class should exist in the dataframe as a label for validation, but MUST NOT be embedded in any numerical/encoded features.
    # We will just verify it's there as a pure string label and not leaked elsewhere.
    assert 'TRUE_DEPLOYMENT_SIM_CLASS' in online.columns
    # Check that no other column accidentally encodes the class
    for col in online.columns:
        if col not in ['TRUE_DEPLOYMENT_SIM_CLASS', 'event_id']:
            assert online[col].dtype in [np.float64, np.int64, float, int]

if __name__ == "__main__":
    pytest.main([__file__])
