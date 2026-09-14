import pandas as pd
import numpy as np
import os
import json

def profile_real_distributions():
    print("Profiling real dataset distributions...")
    os.makedirs('data/processed/deployment_simulation', exist_ok=True)
    
    # We load the real events from Phase 8
    events_df = pd.read_csv('data/interim/events_90d/events.csv')
    
    # Optional files, handled gracefully if they don't exist yet in the workspace state
    try:
        s2_df = pd.read_csv('data/interim/sentinel2/raster_features.csv')
        s2_meta = pd.read_csv('data/interim/sentinel2/evidence_records.csv')
    except:
        s2_df = pd.DataFrame()
        s2_meta = pd.DataFrame()

    profile = {}
    
    # 1. Marginal Quantiles (Continuous)
    def extract_quantiles(series):
        if len(series.dropna()) == 0:
            return [0.0]*11
        return series.dropna().quantile(np.linspace(0, 1, 11)).tolist()
        
    profile['FRP_quantiles'] = extract_quantiles(events_df['mean_frp'])
    profile['duration_hours_quantiles'] = extract_quantiles(events_df['duration_hours'])
    profile['observation_count_quantiles'] = extract_quantiles(events_df['observation_count'])
    
    # 2. Categorical / Frequencies
    s2_missing_rate = 0.85 # Default fallback
    if len(s2_meta) > 0:
        s2_missing_rate = len(s2_meta[s2_meta['evidence'] == 'INSUFFICIENT']) / len(s2_meta)
    profile['sentinel_missing_rate'] = float(s2_missing_rate)
    
    # 3. Covariance / Correlation Structure (Rank Correlation)
    corr_features = ['mean_frp', 'duration_hours', 'observation_count']
    valid_corr_data = events_df[corr_features].dropna()
    
    if len(valid_corr_data) > 10:
        spearman_corr = valid_corr_data.corr(method='spearman').to_dict()
    else:
        spearman_corr = {f: {f2: 1.0 if f == f2 else 0.0 for f2 in corr_features} for f in corr_features}
        
    profile['spearman_rank_correlation'] = spearman_corr
    
    # Save profile
    with open('data/processed/deployment_simulation/real_distribution_profile.json', 'w') as f:
        json.dump(profile, f, indent=4)
        
    print("Real-distribution profile saved.")

if __name__ == "__main__":
    profile_real_distributions()
