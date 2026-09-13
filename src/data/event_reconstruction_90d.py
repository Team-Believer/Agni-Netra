import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.cluster import DBSCAN
import yaml

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    with open('configs/event_reconstruction_90d.yaml', 'r') as f:
        return yaml.safe_load(f)

def haversine_distances(lat, lon):
    # Quick numpy based haversine distance matrix for small to medium sets
    # We will use sklearn BallTree/Haversine directly in the clusterer
    pass

def reconstruct_events():
    config = load_config()
    
    df = pd.read_csv('data/interim/firms_historical_real_normalized.csv')
    
    # 1. Temporal Preprocessing
    # acq_date is YYYY-MM-DD, acq_time is HHMM (often 0-2400)
    def parse_time(row):
        date_str = str(row['acq_date'])
        time_str = str(row['acq_time']).zfill(4)
        if time_str == '2400': time_str = '2359' # Handle 2400 edge case
        dt_str = f"{date_str} {time_str}"
        try:
            return pd.to_datetime(dt_str, format='%Y-%m-%d %H%M')
        except:
            return pd.NaT

    df['utc_timestamp'] = df.apply(parse_time, axis=1)
    df = df.dropna(subset=['utc_timestamp', 'latitude', 'longitude']).copy()
    
    # Validation: Prevent synthetic data
    if any(df['provenance_status'] != 'REAL_SOURCE'):
        raise ValueError("SYNTHETIC DATA DETECTED! Stopping event reconstruction.")
        
    logging.info(f"Processing {len(df)} REAL observations...")
    
    # 2. Spatial Clustering
    # Converting coordinates to radians for haversine
    coords = np.radians(df[['latitude', 'longitude']].values)
    
    # eps in radians (1 km / 6371 km)
    eps_km = config['clustering']['spatial_eps_km']
    eps_rad = eps_km / 6371.0
    
    db = DBSCAN(eps=eps_rad, min_samples=config['clustering']['min_samples'], algorithm='ball_tree', metric='haversine')
    df['spatial_cluster'] = db.fit_predict(coords)
    
    # Generate unique AGN-E IDs
    unique_clusters = df['spatial_cluster'].unique()
    cluster_mapping = {c: f"AGN-E-{i+1:06d}" for i, c in enumerate(unique_clusters) if c != -1}
    # Noise points (-1) get individual IDs
    noise_idx = 1
    
    def assign_id(c):
        nonlocal noise_idx
        if c == -1:
            val = f"AGN-E-N{noise_idx:06d}"
            noise_idx += 1
            return val
        return cluster_mapping[c]
        
    df['event_id'] = df['spatial_cluster'].apply(assign_id)
    
    # Save event_observations
    os.makedirs('data/interim/events_90d', exist_ok=True)
    df.to_csv('data/interim/events_90d/event_observations.csv', index=False)
    
    # 3. Build Events Table
    events = []
    
    for eid, group in df.groupby('event_id'):
        first_detected = group['utc_timestamp'].min()
        last_detected = group['utc_timestamp'].max()
        duration_hours = (last_detected - first_detected).total_seconds() / 3600.0
        
        # Determine State
        if duration_hours > 72:
            state = "Persistent"
        elif duration_hours > 24:
            state = "Escalating"
        else:
            state = "Transient"
            
        satellites_seen = list(group['satellite'].unique())
        
        events.append({
            "event_id": eid,
            "first_detected": first_detected.isoformat(),
            "last_detected": last_detected.isoformat(),
            "centroid_lat": group['latitude'].mean(),
            "centroid_lon": group['longitude'].mean(),
            "observation_count": len(group),
            "duration_hours": duration_hours,
            "mean_frp": group['frp'].mean(),
            "median_frp": group['frp'].median(),
            "max_frp": group['frp'].max(),
            "frp_std": group['frp'].std() if len(group) > 1 else 0.0,
            "satellites_seen": ",".join(satellites_seen),
            "daynight_distribution": dict(group['daynight'].value_counts()) if 'daynight' in group else {},
            "state": state,
            "quality_flag": "OK" if len(group) < 1000 else "EXCESSIVE_OBSERVATIONS"
        })
        
    events_df = pd.DataFrame(events)
    events_df.to_csv('data/interim/events_90d/events.csv', index=False)
    
    # 4. Generate Reports
    os.makedirs('data/processed', exist_ok=True)
    
    report = {
        "real_observations_processed": len(df),
        "unique_days": df['utc_timestamp'].dt.date.nunique(),
        "reconstructed_events": len(events_df),
        "multi_observation_events": int((events_df['observation_count'] > 1).sum()),
        "singleton_events": int((events_df['observation_count'] == 1).sum()),
        "median_event_size": float(events_df['observation_count'].median()),
        "median_duration_hours": float(events_df['duration_hours'].median()),
        "very_long_events": int((events_df['duration_hours'] > 168).sum()),
        "recommended_method": config['clustering']['method'],
        "generated_at": datetime.utcnow().isoformat()
    }
    
    with open('data/processed/event_reconstruction_90d_report.json', 'w') as f:
        json.dump(report, f, indent=4)
        
    logging.info("Event Reconstruction Phase 8A Complete.")

if __name__ == "__main__":
    reconstruct_events()
