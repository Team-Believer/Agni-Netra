import pytest
import numpy as np
from anomaly_engine import robust_mad, analyze_anomaly

def test_robust_mad_zero_variance():
    # Test zero variance
    import pandas as pd
    series = pd.Series([1.0, 1.0, 1.0])
    mad = robust_mad(series)
    assert mad == 0.0

def test_anomaly_thresholds():
    config = {
        'baseline': {
            'highly_abnormal_mad_threshold': 3.5,
            'unusual_mad_threshold': 2.0,
            'min_mad_safeguard': 0.1
        }
    }
    
    # Normal
    score, level = analyze_anomaly(1.0, 1.0, 0.5, config)
    assert level == "NORMAL"
    
    # Unusual
    score, level = analyze_anomaly(2.1, 1.0, 0.5, config)
    assert level == "UNUSUAL"
    
    # Highly Abnormal
    score, level = analyze_anomaly(5.0, 1.0, 0.5, config)
    assert level == "HIGHLY_ABNORMAL"

def test_safeguard_mad():
    config = {
        'baseline': {
            'highly_abnormal_mad_threshold': 3.5,
            'unusual_mad_threshold': 2.0,
            'min_mad_safeguard': 0.1
        }
    }
    # zero mad should be protected
    score, level = analyze_anomaly(1.5, 1.0, 0.0, config)
    # diff = 0.5, safeguard mad = 0.1, score = 5.0 -> HIGHLY_ABNORMAL
    assert score == 5.0
    assert level == "HIGHLY_ABNORMAL"
