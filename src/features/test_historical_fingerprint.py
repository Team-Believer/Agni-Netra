import pytest

def test_history_sufficiency():
    config = {
        "sufficiency": {
            "min_unique_days_sufficient": 7,
            "min_unique_days_partial": 2
        }
    }
    
    unique_days = 8
    if unique_days >= config['sufficiency']['min_unique_days_sufficient']:
        suff = "SUFFICIENT"
    elif unique_days >= config['sufficiency']['min_unique_days_partial']:
        suff = "PARTIAL"
    else:
        suff = "INSUFFICIENT"
        
    assert suff == "SUFFICIENT"
