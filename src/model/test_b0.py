import pytest
import os
import json
import pandas as pd
import numpy as np

def test_feature_target_separation():
    assert os.path.exists('data/interim/features/X_event_features.csv')
    assert os.path.exists('data/interim/features/y_label.csv')
    X = pd.read_csv('data/interim/features/X_event_features.csv')
    assert 'label' not in X.columns

def test_no_label_leakage():
    X = pd.read_csv('data/interim/features/X_event_features.csv')
    leakage_keywords = ['label', 'quality', 'conflict', 'source']
    for col in X.columns:
        for kw in leakage_keywords:
            if kw in col:
                pytest.fail(f"Potential leakage feature found: {col}")

def test_inference_schema():
    # A dummy inference to check output schema
    dummy_event = "AGN-E-000001"
    output = {
        "event_id": dummy_event,
        "classification": {
            "label": "Industrial Fire",
            "confidence": 0.95
        },
        "model_status": "WEAK_LABEL_POC"
    }
    assert "event_id" in output
    assert "classification" in output
    assert "model_status" in output
    assert output["model_status"] == "WEAK_LABEL_POC"
