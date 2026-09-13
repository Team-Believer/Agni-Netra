import os
import yaml
import json
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from datetime import datetime

def load_config():
    with open('configs/event_reconstruction.yaml', 'r') as f:
        return yaml.safe_load(f)

def haversine_distance_matrix(lat, lon):
    # sklearn DBSCAN with haversine expects coordinates in radians (lat, lon)
    coords = np.radians(np.column_stack((lat, lon)))
    return coords

def assign_event_states(group):
    duration_hours = (group['timestamp'].max() - group['timestamp'].min()).total_seconds() / 3600.0
    count = len(group)
    
    if count == 1:
        return "Detected"
    elif duration_hours > 48:
        return "Persistent"
    elif duration_hours > 12:
        return "Emerging"
    else:
        return "Intermittently Observable"

def run_reconstruction():
    config = load_config()
    params = config['clustering_parameters']
    spatial_radius_km = params['spatial_radius_km']
    min_samples = params['minimum_samples']
    gap_hours = params['event_continuation_window']
    
    df = pd.read_csv('data/interim/firms_normalized.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Haversine distance in radians
    epsilon_rad = spatial_radius_km / 6371.0
    coords_rad = np.radians(df[['latitude', 'longitude']].values)
    
    print("Running Spatial DBSCAN (Strategy A)...")
    dbscan = DBSCAN(eps=epsilon_rad, min_samples=min_samples, metric='haversine', algorithm='ball_tree')
    spatial_labels = dbscan.fit_predict(coords_rad)
    
    df['spatial_cluster'] = spatial_labels
    
    # Noise points (-1) become their own singleton clusters
    noise_idx = df['spatial_cluster'] == -1
    max_cluster = df['spatial_cluster'].max()
    df.loc[noise_idx, 'spatial_cluster'] = range(max_cluster + 1, max_cluster + 1 + noise_idx.sum())
    
    # Strategy B: Spatiotemporal (Temporal fragmentation)
    print("Running Temporal Association (Strategy B)...")
    df = df.sort_values(by=['spatial_cluster', 'timestamp']).reset_index(drop=True)
    
    event_ids = []
    current_event_id = 1
    
    for cluster_id, group in df.groupby('spatial_cluster'):
        group = group.sort_values('timestamp')
        prev_time = None
        
        for idx, row in group.iterrows():
            if prev_time is None:
                event_ids.append(current_event_id)
            else:
                time_diff = (row['timestamp'] - prev_time).total_seconds() / 3600.0
                if time_diff > gap_hours:
                    current_event_id += 1 # Split into new event
                event_ids.append(current_event_id)
            prev_time = row['timestamp']
            
        current_event_id += 1
        
    df['event_numeric_id'] = event_ids
    df['event_id'] = df['event_numeric_id'].apply(lambda x: f"AGN-E-{x:06d}")
    
    # Generate Events Schema
    events_data = []
    for event_id, group in df.groupby('event_id'):
        duration = (group['timestamp'].max() - group['timestamp'].min()).total_seconds() / 3600.0
        events_data.append({
            'event_id': event_id,
            'first_detected': group['timestamp'].min().isoformat(),
            'last_detected': group['timestamp'].max().isoformat(),
            'centroid_lat': group['latitude'].mean(),
            'centroid_lon': group['longitude'].mean(),
            'observation_count': len(group),
            'max_frp': group['frp'].max() if 'frp' in group else None,
            'mean_frp': group['frp'].mean() if 'frp' in group else None,
            'frp_std': group['frp'].std() if len(group) > 1 and 'frp' in group else 0.0,
            'duration': duration,
            'satellites_seen': ",".join(group['satellite'].unique().astype(str)) if 'satellite' in group else "",
            'instruments_seen': ",".join(group['instrument'].unique().astype(str)) if 'instrument' in group else "",
            'state': assign_event_states(group),
            'intermittently_observable': duration > 24 and len(group) < (duration/12)
        })
        
    events_df = pd.DataFrame(events_data)
    
    # Save Outputs
    os.makedirs('data/interim/events', exist_ok=True)
    events_df.to_csv('data/interim/events/events.csv', index=False)
    
    obs_assoc = df[['event_id', 'observation_id']].copy()
    obs_assoc['association_score'] = 1.0
    obs_assoc['association_method'] = 'spatial_dbscan_temporal_split'
    obs_assoc.to_csv('data/interim/events/event_observations.csv', index=False)
    
    # Generate Report
    report = {
        "method_tested": "Spatial DBSCAN + Temporal Fragmentation",
        "parameters": params,
        "total_observations": len(df),
        "total_events": len(events_df),
        "singleton_events": int((events_df['observation_count'] == 1).sum()),
        "multi_observation_events": int((events_df['observation_count'] > 1).sum()),
        "median_observations_per_event": float(events_df['observation_count'].median()),
        "median_duration_hours": float(events_df['duration'].median()),
        "max_duration_hours": float(events_df['duration'].max()),
        "intermittent_event_count": int(events_df['intermittently_observable'].sum())
    }
    
    os.makedirs('data/processed', exist_ok=True)
    with open('data/processed/event_reconstruction_report.json', 'w') as f:
        json.dump(report, f, indent=4)
        
    print("Reconstruction complete.")
    print(report)

if __name__ == "__main__":
    run_reconstruction()
