import pytest
import os
import pandas as pd

def test_raw_data_preservation():
    # Original data should exist
    assert os.path.exists('data/interim/firms_normalized.csv')
    
def test_long_window_creation():
    # Long window data should be created in the correct location
    assert os.path.exists('data/raw/firms/long_window/firms_90day.csv')
    df = pd.read_csv('data/raw/firms/long_window/firms_90day.csv')
    assert len(df) > 9714 # Should be larger than the original 7-day dataset

def test_label_quality_assignment():
    # Labels should use Gold/Silver/Bronze structure and default to UNKNOWN or BRONZE
    assert os.path.exists('data/interim/labels_v2/observation_labels_v2.csv')
    labels = pd.read_csv('data/interim/labels_v2/observation_labels_v2.csv')
    assert 'label_quality' in labels.columns
    qualities = labels['label_quality'].unique()
    for q in qualities:
        assert q in ['GOLD', 'SILVER', 'BRONZE', 'UNKNOWN']
        
def test_industrial_facility_without_incident_evidence():
    # In V2, we have zero GOLD industrial fires because we have no incident evidence
    labels = pd.read_csv('data/interim/labels_v2/observation_labels_v2.csv')
    ind_fires = labels[labels['label'] == 'Industrial Fire']
    # Without evidence, they should not exist or be downgraded to unknown. 
    # In our script, they are downgraded to Unknown.
    assert len(ind_fires) == 0
