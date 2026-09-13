import pytest
from sentinel2_raster_corroboration import classify_evidence

def test_evidence_cloud_cover_rejection():
    config = {
        'matching': {
            'max_cloud_cover_percent': 60.0,
            'max_time_delta_hours': 120
        }
    }
    
    # High cloud cover
    ev_status = classify_evidence(True, {'NDVI_contrast': 0.0}, 0.5, 80.0, 10.0, config)
    assert ev_status == "INSUFFICIENT", "High cloud cover must be rejected as INSUFFICIENT, not negative evidence"

def test_insufficient_data():
    config = {
        'matching': {
            'max_cloud_cover_percent': 60.0,
            'max_time_delta_hours': 120
        }
    }
    # Sentinel unavailable / download failed
    ev_status = classify_evidence(False, {}, 0.0, 10.0, 10.0, config)
    assert ev_status == "INSUFFICIENT", "Unavailable image must be INSUFFICIENT"
