import os
import pandas as pd
import numpy as np
import logging
from sklearn.cluster import DBSCAN
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

def reconstruct_events():
    manifest_file = 'data/ground_truth/firms_real_expanded/canonical_observation_manifest.csv'
    out_dir = 'data/ground_truth/events_real_expanded'
    os.makedirs(out_dir, exist_ok=True)
    
    if not os.path.exists(manifest_file):
        logging.error("Canonical manifest not found.")
        return
        
    manifest = pd.read_csv(manifest_file)
    include_files = manifest[manifest['mark'] == 'INCLUDE']['file_path'].tolist()
    
    if not include_files:
        logging.error("No valid INCLUDE files found.")
        return
        
    df_list = []
    for f in include_files:
        if os.path.exists(f):
            try:
                df = pd.read_csv(f)
                # Map product logic back if missing
                # We can just extract it from the filename which is product_date.csv
                fname = os.path.basename(f)
                # Format: VIIRS_NOAA20_SP_2026-01-01.csv
                parts = fname.replace('.csv', '').split('_')
                if len(parts) >= 4:
                    product = f"{parts[0]}_{parts[1]}_{parts[2]}"
                else:
                    product = "UNKNOWN_PRODUCT"
                    
                df['product_source'] = product
                df_list.append(df)
            except Exception as e:
                logging.error(f"Error reading {f}: {e}")
                
    if not df_list:
        return
        
    raw_df = pd.concat(df_list, ignore_index=True)
    # Deduplicate row level to be completely safe
    raw_df = raw_df.drop_duplicates(subset=['latitude', 'longitude', 'acq_date', 'acq_time', 'satellite'])
    
    logging.info(f"Loaded {len(raw_df)} unique observations for event reconstruction.")
    
    raw_df['timestamp'] = pd.to_datetime(raw_df['acq_date'] + ' ' + raw_df['acq_time'].astype(str).str.zfill(4).str.slice(0,2) + ':' + raw_df['acq_time'].astype(str).str.zfill(4).str.slice(2,4))
    
    # Sort for stable clustering
    raw_df = raw_df.sort_values(by='timestamp').reset_index(drop=True)
    
    # We will cluster. Since memory might be an issue with 2.4M rows using DBSCAN in one shot, 
    # we use a spatial grid + time chunking, or a simple grouping logic.
    # For Phase 16GT, we typically rounded coordinates to ~0.015 degrees (1.5km) and grouped by overlapping time windows.
    
    # Instead of full pairwise DBSCAN, let's use a scalable grid-time clustering:
    raw_df['lat_grid'] = raw_df['latitude'].round(2)
    raw_df['lon_grid'] = raw_df['longitude'].round(2)
    raw_df['date_grid'] = raw_df['timestamp'].dt.date
    
    # Group by spatial grid
    grouped = raw_df.groupby(['lat_grid', 'lon_grid'])
    
    events = []
    event_counter = 1
    
    for _, group in grouped:
        group = group.sort_values('timestamp')
        
        current_event_obs = []
        
        for _, row in group.iterrows():
            if not current_event_obs:
                current_event_obs.append(row)
            else:
                last_time = current_event_obs[-1]['timestamp']
                # If gap is > 72 hours, split event (since persistence > 72h is our hard negative threshold, 
                # we want to capture continuous burns. If there's a huge gap, it's a new event).
                if (row['timestamp'] - last_time).total_seconds() / 3600 > 96:
                    # Finalize event
                    ev = finalize_event(current_event_obs, event_counter)
                    events.append(ev)
                    event_counter += 1
                    current_event_obs = [row]
                else:
                    current_event_obs.append(row)
                    
        if current_event_obs:
            ev = finalize_event(current_event_obs, event_counter)
            events.append(ev)
            event_counter += 1
            
    events_df = pd.DataFrame(events)
    events_df.to_csv(f"{out_dir}/real_events.csv", index=False)
    
    report = f"""# Phase 16GT-R2 Event Reconstruction Report

- **Total Observations Processed**: {len(raw_df)}
- **Total Events Reconstructed**: {len(events_df)}
- **Clustering Method**: Spatial Grid (0.01 degree) + Temporal Continuity (96h threshold)
- **Min Duration**: {events_df['duration_hours'].min()}h
- **Max Duration**: {events_df['duration_hours'].max()}h
- **Mean Duration**: {events_df['duration_hours'].mean():.2f}h
"""
    with open('reports/phase16gtr2_event_reconstruction_report.md', 'w') as f:
        f.write(report)
        
    logging.info(f"Reconstructed {len(events_df)} real events.")

def finalize_event(obs_list, ev_id):
    df = pd.DataFrame(obs_list)
    return {
        'event_id': f"REAL-EV-{ev_id:06d}",
        'start_time': df['timestamp'].min(),
        'end_time': df['timestamp'].max(),
        'duration_hours': (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600.0,
        'centroid_lat': df['latitude'].mean(),
        'centroid_lon': df['longitude'].mean(),
        'observation_count': len(df),
        'max_frp': df['frp'].max() if 'frp' in df.columns else 0.0,
        'mean_frp': df['frp'].mean() if 'frp' in df.columns else 0.0,
        'spatial_extent': max(df['latitude'].max() - df['latitude'].min(), df['longitude'].max() - df['longitude'].min()),
        'sensors': ','.join(df['instrument'].unique()) if 'instrument' in df.columns else '',
        'products': ','.join(df['product_source'].unique())
    }

if __name__ == "__main__":
    reconstruct_events()
