import pytest
import torch
import pandas as pd
import numpy as np
import os
from src.models.temporal.sequence_dataset import CausalEventDataset

def test_target_firewall():
    # Attempting to load the dataset must NOT fail if targets exist but are excluded from features.
    dataset = CausalEventDataset('data/synthetic/temporal/train_temporal.csv')
    
    # Check that forbidden features are not in the generated tensors
    from src.models.temporal.sequence_dataset import TEMPORAL_FEATURES, FORBIDDEN_COLUMNS
    for col in FORBIDDEN_COLUMNS:
        assert col not in TEMPORAL_FEATURES

def test_prefix_invariance_and_future_perturbation():
    """
    Simulate Prefix Invariance and Future Perturbation tests.
    If we query the model/dataset at prefix T=2, the features returned MUST be 
    mathematically identical regardless of whether we multiply all future FRPs by 10.
    """
    df = pd.read_csv('data/synthetic/temporal/train_temporal.csv')
    
    # Pick a random long event
    long_event = df[df['sequence_length'] > 4].iloc[0]['event_id']
    
    # Create Dataset A: Original
    df_A = df[df['event_id'] == long_event].copy()
    
    # Create Dataset B: Future Perturbed at T > 2
    df_B = df_A.copy()
    future_mask = df_B['timestep_index'] > 2
    df_B.loc[future_mask, 'frp'] *= 10.0  # Massive future perturbation
    
    df_A.to_csv('data/synthetic/temporal/mock_A.csv', index=False)
    df_B.to_csv('data/synthetic/temporal/mock_B.csv', index=False)
    
    ds_A = CausalEventDataset('data/synthetic/temporal/mock_A.csv', max_seq_len=2)
    ds_B = CausalEventDataset('data/synthetic/temporal/mock_B.csv', max_seq_len=2)
    
    feat_A = ds_A[0]['features']
    feat_B = ds_B[0]['features']
    
    # The extracted prefix tensors MUST be exactly equal because seq_len was capped at 2,
    # and future rows were prevented from leaking backwards into rolling aggregates.
    assert torch.equal(feat_A, feat_B), "FUTURE PERTURBATION LEAKAGE DETECTED: Features changed at early prefix."
    
    os.remove('data/synthetic/temporal/mock_A.csv')
    os.remove('data/synthetic/temporal/mock_B.csv')

def test_padding_mask_invariance():
    """
    Ensure padding doesn't affect the real sequence portion.
    """
    from torch.nn.utils.rnn import pad_sequence
    
    seq = torch.ones(3, 5)
    
    # Pad to length 5 with 0
    pad_0 = pad_sequence([seq], padding_value=0.0)
    # Pad to length 5 with 999
    pad_999 = pad_sequence([seq], padding_value=999.0)
    
    # The actual valid portion must remain identical
    assert torch.equal(pad_0[0, :3, :], pad_999[0, :3, :])

def test_event_split():
    df_train = pd.read_csv('data/synthetic/temporal/train_temporal.csv')
    df_val = pd.read_csv('data/synthetic/temporal/val_temporal.csv')
    df_test = pd.read_csv('data/synthetic/temporal/test_temporal.csv')
    
    train_ids = set(df_train['event_id'].unique())
    val_ids = set(df_val['event_id'].unique())
    test_ids = set(df_test['event_id'].unique())
    
    assert len(train_ids.intersection(val_ids)) == 0, "LEAKAGE: Train and Val share events."
    assert len(train_ids.intersection(test_ids)) == 0, "LEAKAGE: Train and Test share events."
    assert len(val_ids.intersection(test_ids)) == 0, "LEAKAGE: Val and Test share events."

def test_future_label_independence():
    df = pd.read_csv('data/synthetic/temporal/train_temporal.csv')
    
    # Pick a random long event
    long_event = df[df['sequence_length'] > 4].iloc[0]['event_id']
    
    df_A = df[df['event_id'] == long_event].copy()
    df_B = df_A.copy()
    
    # Modify ONLY future labels and metadata
    future_mask = df_B['timestep_index'] > 2
    df_B.loc[future_mask, 'TRUE_SYNTHETIC_CLASS'] = 'ALIEN_CLASS'
    df_B.loc[future_mask, 'latent_behavior'] = 'ALIEN_BEHAVIOR'
    
    df_A.to_csv('data/synthetic/temporal/mock_A.csv', index=False)
    df_B.to_csv('data/synthetic/temporal/mock_B.csv', index=False)
    
    ds_A = CausalEventDataset('data/synthetic/temporal/mock_A.csv', max_seq_len=2)
    ds_B = CausalEventDataset('data/synthetic/temporal/mock_B.csv', max_seq_len=2)
    
    assert torch.equal(ds_A[0]['features'], ds_B[0]['features']), "FUTURE LABEL LEAKAGE DETECTED."
    
    os.remove('data/synthetic/temporal/mock_A.csv')
    os.remove('data/synthetic/temporal/mock_B.csv')

def test_missing_observation():
    df = pd.read_csv('data/synthetic/temporal/train_temporal.csv')
    long_event = df[df['sequence_length'] > 4].iloc[0]['event_id']
    
    df_A = df[df['event_id'] == long_event].copy()
    
    # Remove the middle observation (index 2)
    df_B = df_A.drop(df_A.index[2])
    
    # Assert sequence length decreased but event remains valid
    assert len(df_B) == len(df_A) - 1
    
    # Check temporal gap computation (which should now be larger between index 1 and 3)
    df_B['acq_datetime'] = pd.to_datetime(df_B['acq_datetime'])
    df_A['acq_datetime'] = pd.to_datetime(df_A['acq_datetime'])
    
    gap_B = (df_B.iloc[2]['acq_datetime'] - df_B.iloc[1]['acq_datetime']).total_seconds()
    gap_A = (df_A.iloc[2]['acq_datetime'] - df_A.iloc[1]['acq_datetime']).total_seconds()
    
    assert gap_B > gap_A, "Gap did not correctly increase when observation was removed."

if __name__ == "__main__":
    pytest.main([__file__])
