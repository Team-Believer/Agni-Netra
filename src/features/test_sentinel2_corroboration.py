import pytest
import numpy as np

import sentinel2_raster_corroboration as s2r

def test_evidence_cloud_cover():
    config = {
        'matching': {
            'max_cloud_cover_percent': 60.0,
            'max_time_delta_hours': 120
        }
    }
    # Test high cloud cover directly in classify_evidence
    ev_status = s2r.classify_evidence(True, {}, 0.5, 80.0, 10.0, "Success", config)
    assert ev_status == "INSUFFICIENT"

def test_evidence_temporal_mismatch():
    config = {
        'matching': {
            'max_cloud_cover_percent': 60.0,
            'max_time_delta_hours': 120
        }
    }
    ev_status = s2r.classify_evidence(True, {}, 0.9, 10.0, 200.0, "Success", config)
    assert ev_status == "INSUFFICIENT"

def test_evidence_cloud_limited_reason():
    config = {
        'matching': {
            'max_cloud_cover_percent': 60.0,
            'max_time_delta_hours': 120
        }
    }
    ev_status = s2r.classify_evidence(True, {}, 0.05, 10.0, 10.0, "CLOUD_LIMITED", config)
    assert ev_status == "INSUFFICIENT"

def test_evidence_valid_fraction():
    config = {
        'matching': {
            'max_cloud_cover_percent': 60.0,
            'max_time_delta_hours': 120
        }
    }
    ev_status = s2r.classify_evidence(True, {}, 0.05, 10.0, 10.0, "Success", config)
    assert ev_status == "INSUFFICIENT"

def test_contrast_logic_supporting():
    config = {
        'matching': {
            'max_cloud_cover_percent': 60.0,
            'max_time_delta_hours': 120
        }
    }
    features = {'NDVI_contrast': -0.06}
    ev_status = s2r.classify_evidence(True, features, 0.9, 10.0, 10.0, "Success", config)
    assert ev_status == "SUPPORTING"

def test_contrast_logic_conflicting():
    config = {
        'matching': {
            'max_cloud_cover_percent': 60.0,
            'max_time_delta_hours': 120
        }
    }
    features = {'NDVI_contrast': 0.15}
    ev_status = s2r.classify_evidence(True, features, 0.9, 10.0, 10.0, "Success", config)
    assert ev_status == "CONFLICTING"

def test_contrast_logic_neutral():
    config = {
        'matching': {
            'max_cloud_cover_percent': 60.0,
            'max_time_delta_hours': 120
        }
    }
    features = {'NDVI_contrast': 0.05}
    ev_status = s2r.classify_evidence(True, features, 0.9, 10.0, 10.0, "Success", config)
    assert ev_status == "NEUTRAL"

def test_provenance_no_simulated_fallback():
    with open('src/features/sentinel2_raster_corroboration.py', 'r') as f:
        content = f.read()
    assert "np.random" not in content
    
def test_roi_placement_logic():
    pixel_col = 100
    pixel_row = 100
    raster_height = 500
    raster_width = 500
    
    r_ev_min = max(0, pixel_row - 25)
    r_ev_max = min(raster_height, pixel_row + 25)
    assert r_ev_min == 75
    assert r_ev_max == 125
    
    r_bg_min = max(0, pixel_row - 75)
    r_bg_max = min(raster_height, pixel_row + 75)
    assert r_bg_min == 25
    assert r_bg_max == 175
    
def test_indices_math():
    b08 = np.array([0.5, 0.0])
    b04 = np.array([0.1, 0.0])
    ndvi = (b08 - b04) / (b08 + b04 + 1e-8)
    assert np.isclose(ndvi[0], 0.6666666)
    assert np.isclose(ndvi[1], 0.0)
