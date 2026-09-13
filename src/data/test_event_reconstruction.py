import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Simplified mock of the reconstruction logic for testing core requirements
def mock_reconstruct(observations, radius_km, gap_hours):
    # Observations: list of dicts with lat, lon, timestamp, sat
    from sklearn.cluster import DBSCAN
    
    if not observations: return []
    df = pd.DataFrame(observations)
    
    # Invalid coordinates check
    valid = (df['lat'] >= -90) & (df['lat'] <= 90) & (df['lon'] >= -180) & (df['lon'] <= 180)
    df = df[valid].copy()
    if df.empty: return []
    
    epsilon_rad = radius_km / 6371.0
    coords_rad = np.radians(df[['lat', 'lon']].values)
    
    dbscan = DBSCAN(eps=epsilon_rad, min_samples=1, metric='haversine', algorithm='ball_tree')
    df['spatial_cluster'] = dbscan.fit_predict(coords_rad)
    
    df = df.sort_values(by=['spatial_cluster', 'timestamp']).reset_index(drop=True)
    
    events = []
    current_event = 1
    
    for cluster_id, group in df.groupby('spatial_cluster'):
        prev_time = None
        for idx, row in group.iterrows():
            if prev_time is not None:
                time_diff = (row['timestamp'] - prev_time).total_seconds() / 3600.0
                if time_diff > gap_hours:
                    current_event += 1
            events.append({"obs_id": row['obs_id'], "event_id": current_event})
            prev_time = row['timestamp']
        current_event += 1
        
    return pd.DataFrame(events)

def test_close_space_time():
    t0 = datetime(2026, 9, 10, 12, 0)
    obs = [
        {"obs_id": 1, "lat": 22.0, "lon": 70.0, "timestamp": t0},
        {"obs_id": 2, "lat": 22.001, "lon": 70.001, "timestamp": t0 + timedelta(hours=1)}
    ]
    res = mock_reconstruct(obs, 1.0, 72)
    assert res['event_id'].iloc[0] == res['event_id'].iloc[1]

def test_far_apart():
    t0 = datetime(2026, 9, 10, 12, 0)
    obs = [
        {"obs_id": 1, "lat": 22.0, "lon": 70.0, "timestamp": t0},
        {"obs_id": 2, "lat": 23.0, "lon": 71.0, "timestamp": t0} # ~150km away
    ]
    res = mock_reconstruct(obs, 1.0, 72)
    assert res['event_id'].iloc[0] != res['event_id'].iloc[1]

def test_large_temporal_gap():
    t0 = datetime(2026, 9, 10, 12, 0)
    obs = [
        {"obs_id": 1, "lat": 22.0, "lon": 70.0, "timestamp": t0},
        {"obs_id": 2, "lat": 22.0, "lon": 70.0, "timestamp": t0 + timedelta(hours=100)} # gap > 72h
    ]
    res = mock_reconstruct(obs, 1.0, 72)
    assert res['event_id'].iloc[0] != res['event_id'].iloc[1]

def test_different_satellites():
    t0 = datetime(2026, 9, 10, 12, 0)
    obs = [
        {"obs_id": 1, "lat": 22.0, "lon": 70.0, "timestamp": t0, "sat": "N20"},
        {"obs_id": 2, "lat": 22.0, "lon": 70.0, "timestamp": t0 + timedelta(minutes=50), "sat": "N"}
    ]
    res = mock_reconstruct(obs, 1.0, 72)
    assert res['event_id'].iloc[0] == res['event_id'].iloc[1]

def test_intermittent_observation():
    t0 = datetime(2026, 9, 10, 12, 0)
    obs = [
        {"obs_id": 1, "lat": 22.0, "lon": 70.0, "timestamp": t0},
        {"obs_id": 2, "lat": 22.0, "lon": 70.0, "timestamp": t0 + timedelta(hours=48)} # < 72h gap, preserves ID
    ]
    res = mock_reconstruct(obs, 1.0, 72)
    assert res['event_id'].iloc[0] == res['event_id'].iloc[1]

def test_invalid_coordinates():
    t0 = datetime(2026, 9, 10, 12, 0)
    obs = [
        {"obs_id": 1, "lat": 200.0, "lon": 70.0, "timestamp": t0}, # invalid lat
        {"obs_id": 2, "lat": 22.0, "lon": 70.0, "timestamp": t0}
    ]
    res = mock_reconstruct(obs, 1.0, 72)
    assert len(res) == 1
    assert res['obs_id'].iloc[0] == 2
