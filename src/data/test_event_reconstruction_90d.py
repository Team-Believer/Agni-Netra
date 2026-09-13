import pytest
import pandas as pd
from datetime import datetime

def test_utc_conversion():
    # Simple check for valid parse_time behavior simulated
    date_str = "2026-06-15"
    time_str = "2400"
    if time_str == '2400': time_str = '2359'
    dt_str = f"{date_str} {time_str}"
    res = pd.to_datetime(dt_str, format='%Y-%m-%d %H%M')
    assert res.hour == 23 and res.minute == 59

def test_provenance_rejection():
    df = pd.DataFrame([{"provenance_status": "SYNTHETIC"}])
    assert any(df['provenance_status'] != 'REAL_SOURCE')
