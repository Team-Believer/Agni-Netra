import pytest
import pandas as pd
from src.models.multitask.multitask_dataset import MultiTaskCausalDataset, FORBIDDEN_COLUMNS, TEMPORAL_FEATURES

def test_target_firewall():
    # Ensure no forbidden column is in the feature list
    for col in FORBIDDEN_COLUMNS:
        assert col not in TEMPORAL_FEATURES, f"Target Firewall Breach: {col} is in TEMPORAL_FEATURES"

def test_event_split_integrity():
    train = pd.read_csv('data/synthetic/multitask/train_mt_0.15.csv')
    val = pd.read_csv('data/synthetic/multitask/val_mt_0.15.csv')
    test = pd.read_csv('data/synthetic/multitask/final_holdout_mt.csv')
    
    train_ids = set(train['event_id'].unique())
    val_ids = set(val['event_id'].unique())
    test_ids = set(test['event_id'].unique())
    
    assert len(train_ids.intersection(val_ids)) == 0, "Train and Val overlap!"
    assert len(train_ids.intersection(test_ids)) == 0, "Train and Test overlap!"
    assert len(val_ids.intersection(test_ids)) == 0, "Val and Test overlap!"

def test_holdout_integrity():
    test = pd.read_csv('data/synthetic/multitask/final_holdout_mt.csv')
    assert len(test['event_id'].unique()) == 2000, "Holdout size changed!"
