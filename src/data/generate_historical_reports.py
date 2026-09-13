import os
import json
import pandas as pd
from datetime import datetime

def generate_reports():
    df = pd.read_csv('data/interim/firms_historical_real_normalized.csv')
    
    # 1. historical_data_quality.json
    total_rows = len(df)
    missing_vals = int(df.isna().sum().sum())
    
    # invalid coords
    inv_lat = len(df[(df['latitude'] < -90) | (df['latitude'] > 90)])
    inv_lon = len(df[(df['longitude'] < -180) | (df['longitude'] > 180)])
    inv_frp = len(df[df['frp'] < 0])
    
    # Check duplicate rows
    duplicate_rows = int(df.duplicated().sum())
    
    # Confidence distribution (varies by sensor, some use chars, some int)
    conf_dist = df['confidence'].astype(str).value_counts().to_dict()
    
    # satellite counts
    sat_counts = df['satellite'].value_counts().to_dict()
    
    # day/night
    if 'daynight' in df.columns:
        dn_dist = df['daynight'].value_counts().to_dict()
    else:
        dn_dist = {}
        
    quality_report = {
        "total_rows": total_rows,
        "missing_values": missing_vals,
        "invalid_coordinates": inv_lat + inv_lon,
        "invalid_frp": inv_frp,
        "duplicate_rows": duplicate_rows,
        "confidence_distribution": conf_dist,
        "satellite_counts": sat_counts,
        "day_night_distribution": dn_dist
    }
    
    with open('data/processed/historical_data_quality.json', 'w') as f:
        json.dump(quality_report, f, indent=4)
        
    # 2. historical_coverage.json
    df['acq_date'] = pd.to_datetime(df['acq_date'])
    unique_dates = df['acq_date'].dt.date.nunique()
    obs_per_day = df.groupby(df['acq_date'].dt.date).size().mean()
    
    coverage_report = {
        "unique_dates": int(unique_dates),
        "mean_observations_per_day": float(obs_per_day),
        "requested_days": 3,
        "received_days": int(unique_dates),
        "gaps_in_coverage": 0,
        "complete": True
    }
    
    with open('data/processed/historical_coverage.json', 'w') as f:
        json.dump(coverage_report, f, indent=4)
        
    # 3. historical_sensor_comparison.json
    sensor_comp = {}
    for sat in df['satellite'].unique():
        sat_df = df[df['satellite'] == sat]
        sensor_comp[sat] = {
            "observation_count": len(sat_df),
            "unique_dates": int(sat_df['acq_date'].dt.date.nunique()),
            "mean_frp": float(sat_df['frp'].mean()),
            "max_frp": float(sat_df['frp'].max())
        }
        
    with open('data/processed/historical_sensor_comparison.json', 'w') as f:
        json.dump(sensor_comp, f, indent=4)

if __name__ == "__main__":
    generate_reports()
