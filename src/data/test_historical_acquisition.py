import pytest
import os
import pandas as pd
from dotenv import load_dotenv

def test_credential_loading():
    load_dotenv()
    assert os.getenv('MAP_KEY') is not None

def test_no_secret_leakage():
    with open('src/data/acquire_firms_historical.py', 'r') as f:
        content = f.read()
    assert "os.getenv('MAP_KEY')" in content
    assert "print(map_key)" not in content

def test_synthetic_data_rejection():
    # Verify no synthetic duplicate files snuck into historical_real
    if os.path.exists('data/raw/firms/historical_real'):
        files = os.listdir('data/raw/firms/historical_real')
        for f in files:
            assert 'firms_90day' not in f

def test_provenance_validation():
    if os.path.exists('data/interim/firms_historical_real_normalized.csv'):
        df = pd.read_csv('data/interim/firms_historical_real_normalized.csv')
        assert 'provenance_status' in df.columns
        assert all(df['provenance_status'] == 'REAL_SOURCE')
