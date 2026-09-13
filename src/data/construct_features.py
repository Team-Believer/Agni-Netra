import os
import json
import pandas as pd
import numpy as np

def compute_spatial_spread(lats, lons):
    if len(lats) < 2: return 0.0
    # Simple approx max distance (bounding box diagonal)
    lat_diff = (max(lats) - min(lats)) * 111.0 # roughly km
    lon_diff = (max(lons) - min(lons)) * 111.0 * np.cos(np.radians(np.mean(lats)))
    return np.sqrt(lat_diff**2 + lon_diff**2)

def aggregate_labels(group):
    # Rule: consistent observation labels -> event label
    # conflicting -> UNKNOWN / AMBIGUOUS
    unique_labels = group['label'].dropna().unique()
    unique_labels = [l for l in unique_labels if l != "Unknown / Needs Verification"]
    
    if len(unique_labels) == 1:
        return unique_labels[0], "WEAK_AGGREGATED" # Default to weak for aggregates
    elif len(unique_labels) > 1:
        return "Unknown / Needs Verification", "AMBIGUOUS"
    else:
        return "Unknown / Needs Verification", "UNKNOWN"

def build_features():
    print("Loading data...")
    events = pd.read_csv('data/interim/events/events.csv')
    obs = pd.read_csv('data/interim/firms_normalized.csv')
    obs['timestamp'] = pd.to_datetime(obs['timestamp'])
    
    event_obs = pd.read_csv('data/interim/events/event_observations.csv')
    
    try:
        labels_df = pd.read_csv('data/interim/labels/observation_labels.csv')
    except:
        labels_df = pd.DataFrame(columns=['observation_id', 'label', 'label_quality'])
        
    print("Merging data...")
    # Merge obs with event association
    merged = pd.merge(event_obs, obs, on='observation_id', how='left')
    # Merge labels
    merged = pd.merge(merged, labels_df[['observation_id', 'label', 'label_quality']], on='observation_id', how='left')
    
    features = []
    
    print("Computing features...")
    # Compute event-level labels first
    event_labels = merged.groupby('event_id').apply(aggregate_labels).reset_index(name='label_tuple')
    event_labels['label'] = event_labels['label_tuple'].apply(lambda x: x[0])
    event_labels['label_quality'] = event_labels['label_tuple'].apply(lambda x: x[1])
    event_labels = event_labels.drop(columns=['label_tuple'])
    
    # Define mapping for confidence
    conf_map = {'low': 1, 'nominal': 2, 'high': 3, 'l': 1, 'n': 2, 'h': 3}
    merged['conf_num'] = merged['confidence'].str.lower().map(conf_map).fillna(2)
    
    for event_id, group in merged.groupby('event_id'):
        group = group.sort_values('timestamp')
        
        # Thermal
        frps = group['frp'].dropna()
        brights = group['brightness'].dropna()
        
        mean_frp = frps.mean() if not frps.empty else np.nan
        max_frp = frps.max() if not frps.empty else np.nan
        min_frp = frps.min() if not frps.empty else np.nan
        frp_std = frps.std() if len(frps) > 1 else 0.0
        frp_cv = (frp_std / mean_frp) if mean_frp > 0 else 0.0
        
        frp_first = frps.iloc[0] if not frps.empty else np.nan
        frp_last = frps.iloc[-1] if not frps.empty else np.nan
        frp_change = frp_last - frp_first if not frps.empty else 0.0
        
        # Temporal
        times = group['timestamp']
        duration = (times.max() - times.min()).total_seconds() / 3600.0
        obs_count = len(group)
        obs_per_day = obs_count / max((duration / 24.0), 1.0)
        
        gaps = times.diff().dt.total_seconds().dropna() / 3600.0
        median_gap = gaps.median() if not gaps.empty else 0.0
        max_gap = gaps.max() if not gaps.empty else 0.0
        
        day_night = group['daynight'].value_counts() if 'daynight' in group else {}
        day_count = day_night.get('D', 0)
        night_count = day_night.get('N', 0)
        day_night_ratio = day_count / (day_count + night_count) if (day_count + night_count) > 0 else 0.5
        
        # Spatial
        lats = group['latitude']
        lons = group['longitude']
        spread = compute_spatial_spread(lats.tolist(), lons.tolist())
        
        # Sensor
        num_sat = group['satellite'].nunique() if 'satellite' in group else 1
        
        # Behavior
        expanding = int(spread > 0.5 and obs_count > 1)
        stable = int(spread < 0.1)
        sudden_inc = int(max_frp > 3 * mean_frp) if pd.notna(mean_frp) and mean_frp > 0 else 0
        
        # Quality
        min_conf = group['conf_num'].min()
        mean_conf = group['conf_num'].mean()
        
        features.append({
            'event_id': event_id,
            # Features
            'mean_frp': mean_frp,
            'max_frp': max_frp,
            'min_frp': min_frp,
            'frp_std': frp_std,
            'frp_cv': frp_cv,
            'frp_first': frp_first,
            'frp_last': frp_last,
            'frp_change': frp_change,
            'brightness_mean': brights.mean() if not brights.empty else np.nan,
            'brightness_max': brights.max() if not brights.empty else np.nan,
            
            'duration_hours': duration,
            'observation_count': obs_count,
            'obs_per_day': obs_per_day,
            'median_gap': median_gap,
            'max_gap': max_gap,
            'day_night_ratio': day_night_ratio,
            
            'spatial_spread_km': spread,
            
            'num_satellites': num_sat,
            
            'expanding_indicator': expanding,
            'stable_indicator': stable,
            'sudden_frp_increase': sudden_inc,
            
            'min_confidence': min_conf,
            'mean_confidence': mean_conf,
            
            'history_window_days': 7,
            'history_sufficiency': 'INSUFFICIENT'
        })
        
    feat_df = pd.DataFrame(features)
    
    # Merge label safely
    final_df = pd.merge(event_labels, feat_df, on='event_id')
    
    # Order columns: event_id, label, label_quality, ...features
    cols = ['event_id', 'label', 'label_quality'] + [c for c in final_df.columns if c not in ['event_id', 'label', 'label_quality']]
    final_df = final_df[cols]
    
    os.makedirs('data/interim/features', exist_ok=True)
    final_df.to_csv('data/interim/features/event_features.csv', index=False)
    
    # Separate ML matrices
    X = final_df.drop(columns=['label', 'label_quality'])
    y = final_df[['event_id', 'label', 'label_quality']]
    
    X.to_csv('data/interim/features/X_event_features.csv', index=False)
    y.to_csv('data/interim/features/y_label.csv', index=False)
    
    # Feature Dictionary
    fdict = [
        {"feature_name": "mean_frp", "group": "THERMAL", "type": "float", "missingness": float(X['mean_frp'].isna().mean()), "leakage_risk": "LOW (Offline assumption)"},
        {"feature_name": "duration_hours", "group": "TEMPORAL", "type": "float", "missingness": float(X['duration_hours'].isna().mean()), "leakage_risk": "HIGH (Full event history required)"}
    ]
    with open('data/interim/features/feature_dictionary.json', 'w') as f:
        json.dump(fdict, f, indent=4)
        
    # Quality Audit Report
    report = {
        "total_events": len(final_df),
        "total_features": len(X.columns) - 1,
        "missingness": X.isna().mean().to_dict(),
        "constant_features": [c for c in X.columns if X[c].nunique() <= 1 and c != 'event_id'],
        "label_distribution": y['label'].value_counts().to_dict(),
        "label_quality_distribution": y['label_quality'].value_counts().to_dict()
    }
    with open('data/interim/features/feature_quality_report.json', 'w') as f:
        json.dump(report, f, indent=4)
        
    print("Feature generation complete.")
    print(report)

if __name__ == "__main__":
    build_features()
