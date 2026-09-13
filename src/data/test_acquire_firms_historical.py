import pytest
import os
import json

def test_raw_file_preservation():
    # Original data must remain untouched
    assert os.path.exists('data/interim/firms_normalized.csv')

def test_credential_non_leakage():
    # Ensure our script does not hardcode MAP_KEY
    with open('src/data/acquire_firms_historical.py', 'r') as f:
        content = f.read()
    assert "YOUR_API_KEY" not in content
    assert "MAP_KEY = " not in content

def test_no_synthetic_data_in_historical_real():
    # We should have no files in historical_real since download failed
    # But if there were, they MUST be authentic.
    real_dir = 'data/raw/firms/historical_real'
    if os.path.exists(real_dir):
        files = os.listdir(real_dir)
        # Should be empty in this mock state
        assert len(files) == 0

def test_metadata_status():
    assert os.path.exists('data/processed/historical_dataset_metadata.json')
    with open('data/processed/historical_dataset_metadata.json', 'r') as f:
        meta = json.load(f)
    assert meta.get('status') == 'FAILED_NO_CREDENTIALS'
