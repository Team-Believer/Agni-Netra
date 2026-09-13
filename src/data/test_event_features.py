import pytest
import pandas as pd
import numpy as np

# We'll test the core logic functions used in construct_features.py
from construct_features import aggregate_labels, compute_spatial_spread

def test_aggregate_labels_consistent():
    group = pd.DataFrame({'label': ['Industrial Fire', 'Industrial Fire']})
    lbl, qual = aggregate_labels(group)
    assert lbl == 'Industrial Fire'
    assert qual == 'WEAK_AGGREGATED'
    
def test_aggregate_labels_conflicting():
    group = pd.DataFrame({'label': ['Industrial Fire', 'Wildfire']})
    lbl, qual = aggregate_labels(group)
    assert lbl == 'Unknown / Needs Verification'
    assert qual == 'AMBIGUOUS'

def test_aggregate_labels_unknown():
    group = pd.DataFrame({'label': ['Unknown / Needs Verification', 'Unknown / Needs Verification']})
    lbl, qual = aggregate_labels(group)
    assert lbl == 'Unknown / Needs Verification'
    assert qual == 'UNKNOWN'

def test_compute_spatial_spread_single_obs():
    spread = compute_spatial_spread([22.0], [70.0])
    assert spread == 0.0

def test_compute_spatial_spread_multi_obs():
    spread = compute_spatial_spread([22.0, 22.01], [70.0, 70.01])
    assert spread > 0.0

def test_no_label_leakage():
    # Verify that the generated X_event_features.csv does not contain label columns
    import os
    if os.path.exists('data/interim/features/X_event_features.csv'):
        X = pd.read_csv('data/interim/features/X_event_features.csv')
        assert 'label' not in X.columns
        assert 'label_quality' not in X.columns
        assert 'label_reason' not in X.columns
