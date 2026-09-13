import os
import json
import pandas as pd
import ast

def inspect_code():
    # Read expand_dataset.py to find how data was generated
    script_path = 'src/data/expand_dataset.py'
    if not os.path.exists(script_path):
        return "Script not found."
    
    with open(script_path, 'r') as f:
        content = f.read()
        
    generation_method = []
    if "timedelta" in content and "day_offset" in content:
        generation_method.append("Date shifting")
    if "np.random.rand()" in content or "np.random.uniform" in content:
        generation_method.append("Random generation / FRP modification")
    if "row.copy()" in content and "new_obs.append" in content:
        generation_method.append("Pandas duplication (row replication)")
    
    return generation_method

def audit_datasets():
    short_path = 'data/interim/firms_normalized.csv'
    long_path = 'data/raw/firms/long_window/firms_90day.csv'
    
    df_short = pd.read_csv(short_path)
    df_long = pd.read_csv(long_path)
    
    real_count = len(df_short)
    total_long_count = len(df_long)
    synthetic_count = total_long_count - real_count
    
    df_long['timestamp'] = pd.to_datetime(df_long['timestamp'])
    
    unique_dates = df_long['timestamp'].dt.date.nunique()
    earliest = df_long['timestamp'].min().isoformat()
    latest = df_long['timestamp'].max().isoformat()
    
    # Trace duplicates
    # Since we copied coordinates exactly, any coord pair in long that appears more times than in short is a synthetic duplicate
    long_coords = df_long.groupby(['latitude', 'longitude']).size()
    short_coords = df_short.groupby(['latitude', 'longitude']).size()
    
    duplicate_coords_count = (long_coords > short_coords).sum()
    
    report = {
        "generation_method": inspect_code(),
        "files_audited": [
            {"path": long_path, "source": "Synthetic expansion script", "authenticity": "SYNTHETIC_DERIVED"}
        ],
        "authenticity": {
            "seven_day_dataset": "REAL_SOURCE (assumed from Phase 2 FIRMS acquisition)",
            "ninety_day_dataset": "SYNTHETIC"
        },
        "counts": {
            "real_observations": real_count,
            "synthetic_observations": synthetic_count,
            "total_observations": total_long_count
        },
        "date_distribution": {
            "unique_dates": int(unique_dates),
            "earliest_timestamp": earliest,
            "latest_timestamp": latest
        },
        "duplication": {
            "locations_with_synthetic_duplicates": int(duplicate_coords_count)
        },
        "location_claim_audit": {
            "claim": "919 geographic locations have >50 observations over 90 days.",
            "validity": "INVALID. The 90-day data was synthesized by copying the 7-day data backwards in time with random survival probability. The 919 locations are entirely an artifact of this replication."
        }
    }
    
    os.makedirs('data/processed', exist_ok=True)
    with open('data/processed/long_window_authenticity_report.json', 'w') as f:
        json.dump(report, f, indent=4)
        
    return report

if __name__ == "__main__":
    rep = audit_datasets()
    print(json.dumps(rep, indent=2))
