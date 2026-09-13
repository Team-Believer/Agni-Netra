import os
import glob
import pandas as pd
import numpy as np
import json
from datetime import datetime
from sklearn.neighbors import NearestNeighbors

def inspect_data():
    raw_dir = 'data/raw/firms'
    csv_files = glob.glob(os.path.join(raw_dir, '*_7d.csv'))
    
    if not csv_files:
        print("No CSV files found.")
        return

    dfs = []
    for f in csv_files:
        sensor = os.path.basename(f).split('_')[0]
        df = pd.read_csv(f)
        df['source_file'] = os.path.basename(f)
        dfs.append(df)
        
    combined_df = pd.concat(dfs, ignore_index=True)
    
    report = {}
    
    # B. Dataset statistics
    report['total_rows'] = len(combined_df)
    report['geographic_coverage'] = {
        'lat_min': float(combined_df['latitude'].min()),
        'lat_max': float(combined_df['latitude'].max()),
        'lon_min': float(combined_df['longitude'].min()),
        'lon_max': float(combined_df['longitude'].max())
    }
    
    # Handle timestamps: 'acq_date' and 'acq_time' are usually in FIRMS
    if 'acq_date' in combined_df.columns and 'acq_time' in combined_df.columns:
        # acq_time is often HHMM integer or string. Let's pad it to 4 chars
        combined_df['acq_time_str'] = combined_df['acq_time'].astype(str).str.zfill(4)
        combined_df['timestamp'] = pd.to_datetime(combined_df['acq_date'] + ' ' + combined_df['acq_time_str'], format='%Y-%m-%d %H%M')
        report['temporal_coverage'] = {
            'min': combined_df['timestamp'].min().isoformat(),
            'max': combined_df['timestamp'].max().isoformat()
        }
    
    report['satellites'] = combined_df['satellite'].unique().tolist() if 'satellite' in combined_df.columns else []
    report['instruments'] = combined_df['instrument'].unique().tolist() if 'instrument' in combined_df.columns else []
    
    # C. Schema findings
    schema = {}
    for col in combined_df.columns:
        schema[col] = {
            'type': str(combined_df[col].dtype),
            'missing': int(combined_df[col].isna().sum())
        }
    report['schema'] = schema
    
    # D. Data quality
    quality = {}
    quality['invalid_coords'] = int(((combined_df['latitude'] < -90) | (combined_df['latitude'] > 90) | (combined_df['longitude'] < -180) | (combined_df['longitude'] > 180)).sum())
    if 'frp' in combined_df.columns:
        quality['invalid_frp'] = int((combined_df['frp'] < 0).sum())
    report['quality'] = quality
    
    # E. Spatial Analysis
    # Let's take a sample of 10000 to compute nearest neighbors to avoid memory issues
    sample_df = combined_df.sample(min(10000, len(combined_df)))
    # Convert lat/lon to radians for haversine
    coords = np.radians(sample_df[['latitude', 'longitude']])
    nbrs = NearestNeighbors(n_neighbors=2, metric='haversine').fit(coords)
    distances, _ = nbrs.kneighbors(coords)
    # Haversine distance in radians * Earth radius in km (6371)
    distances_km = distances[:, 1] * 6371
    report['spatial'] = {
        'median_nearest_neighbor_km': float(np.median(distances_km)),
        'mean_nearest_neighbor_km': float(np.mean(distances_km)),
        'dense_clusters_under_1km': int((distances_km < 1.0).sum())
    }
    
    # F. Temporal Analysis
    if 'timestamp' in combined_df.columns:
        report['temporal'] = {
            'detections_per_day': combined_df['timestamp'].dt.date.value_counts().to_dict(),
            'day_night_split': combined_df['daynight'].value_counts().to_dict() if 'daynight' in combined_df.columns else {}
        }
    else:
        report['temporal'] = {}
        
    # G. Sensor Comparison
    if 'satellite' in combined_df.columns:
        report['sensors'] = combined_df.groupby('satellite').size().to_dict()
    else:
        report['sensors'] = {}
        
    # Save report
    os.makedirs('data/processed', exist_ok=True)
    
    # Ensure datetime objects in dictionary are converted to string before dumping
    # handled mostly by manual conversion above, but let's be careful with detections_per_day keys
    if 'temporal' in report and 'detections_per_day' in report['temporal']:
        report['temporal']['detections_per_day'] = {str(k): v for k, v in report['temporal']['detections_per_day'].items()}
        
    with open('data/processed/inspection_report.json', 'w') as f:
        json.dump(report, f, indent=4)
        
    # Create Normalized Dataset
    # observation_id timestamp latitude longitude frp brightness confidence satellite instrument source product_version
    norm_cols = {}
    norm_cols['observation_id'] = [f"obs_{i}" for i in range(len(combined_df))]
    if 'timestamp' in combined_df.columns: norm_cols['timestamp'] = combined_df['timestamp']
    if 'latitude' in combined_df.columns: norm_cols['latitude'] = combined_df['latitude']
    if 'longitude' in combined_df.columns: norm_cols['longitude'] = combined_df['longitude']
    if 'frp' in combined_df.columns: norm_cols['frp'] = combined_df['frp']
    if 'bright_ti4' in combined_df.columns: norm_cols['brightness'] = combined_df['bright_ti4'] # VIIRS brightness
    if 'confidence' in combined_df.columns: norm_cols['confidence'] = combined_df['confidence']
    if 'satellite' in combined_df.columns: norm_cols['satellite'] = combined_df['satellite']
    if 'instrument' in combined_df.columns: norm_cols['instrument'] = combined_df['instrument']
    if 'version' in combined_df.columns: norm_cols['product_version'] = combined_df['version']
    norm_cols['source'] = combined_df['source_file']
    
    norm_df = pd.DataFrame(norm_cols)
    os.makedirs('data/interim', exist_ok=True)
    norm_df.to_csv('data/interim/firms_normalized.csv', index=False)
    
    print("Inspection complete. Saved to data/processed/inspection_report.json and data/interim/firms_normalized.csv")

if __name__ == "__main__":
    inspect_data()
