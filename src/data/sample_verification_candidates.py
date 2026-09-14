import pandas as pd
import numpy as np
import os
import json

def run_sampling():
    os.makedirs('data/labels', exist_ok=True)
    
    # 1. Load Data
    events_df = pd.read_csv('data/interim/events_90d/events.csv')
    try:
        anom_df = pd.read_csv('data/processed/anomaly_scores_90d.csv')
    except:
        anom_df = pd.DataFrame(columns=['event_id', 'anomaly.score'])
        
    gov_df = pd.read_csv('data/processed/b2/label_governance.csv')
    
    try:
        s2_df = pd.read_csv('data/interim/sentinel2/evidence_records.csv')
        s2_events = set(s2_df[s2_df['evidence'] != 'INSUFFICIENT']['event_id'])
    except:
        s2_events = set()
        
    # Merge basic features
    df = pd.merge(events_df, gov_df[['event_id', 'class', 'label_type']], on='event_id', how='left')
    df = pd.merge(df, anom_df[['event_id', 'anomaly.score']], on='event_id', how='left')
    
    # 2. Tag Strata (Events can have multiple tags)
    df['is_high_anomaly'] = df['anomaly.score'] >= df['anomaly.score'].quantile(0.90)
    df['is_bronze_industrial'] = (df['class'] == 'Industrial Fire') & (df['label_type'] == 'WEAK')
    df['is_bronze_flare'] = (df['class'] == 'Routine Flare') & (df['label_type'] == 'WEAK')
    df['is_bronze_wildfire_ag'] = (df['class'].isin(['Wildfire', 'Agricultural Burn'])) & (df['label_type'] == 'WEAK')
    df['is_sentinel_avail'] = df['event_id'].isin(s2_events)
    df['is_persistent'] = (df['duration_hours'] > 72) & (df['class'] == 'UNKNOWN')
    df['is_singleton'] = (df['observation_count'] == 1) & (df['class'] == 'UNKNOWN')
    df['is_random_unknown'] = df['class'] == 'UNKNOWN'
    
    # 3. Deterministic Sampling Target Definition
    targets = {
        'is_high_anomaly': 60,
        'is_bronze_industrial': 30,
        'is_bronze_flare': 30,
        'is_bronze_wildfire_ag': 30,
        'is_sentinel_avail': 30,
        'is_persistent': 45,
        'is_singleton': 30,
        'is_random_unknown': 45
    }
    
    selected_indices = set()
    np.random.seed(42) # Reproducibility
    
    # Helper to sample without exceeding population or target
    def sample_stratum(condition_col, target):
        pool = df[(df[condition_col] == True) & (~df.index.isin(selected_indices))].index
        n_to_sample = min(target, len(pool))
        if n_to_sample > 0:
            chosen = np.random.choice(pool, size=n_to_sample, replace=False)
            selected_indices.update(chosen)
            
    # Sample in priority order (rarest classes first)
    sample_stratum('is_bronze_industrial', targets['is_bronze_industrial'])
    sample_stratum('is_bronze_flare', targets['is_bronze_flare'])
    sample_stratum('is_bronze_wildfire_ag', targets['is_bronze_wildfire_ag'])
    sample_stratum('is_sentinel_avail', targets['is_sentinel_avail'])
    sample_stratum('is_high_anomaly', targets['is_high_anomaly'])
    sample_stratum('is_persistent', targets['is_persistent'])
    sample_stratum('is_singleton', targets['is_singleton'])
    
    # Fill remaining slots up to 300 with random background
    remaining_slots = 300 - len(selected_indices)
    if remaining_slots > 0:
        sample_stratum('is_random_unknown', remaining_slots)
        
    candidates = df.loc[list(selected_indices)].copy()
    
    # Assign Blind Review Mode (20% of 300 = 60)
    candidates['blind_review_mode'] = False
    blind_idx = np.random.choice(candidates.index, size=int(len(candidates)*0.2), replace=False)
    candidates.loc[blind_idx, 'blind_review_mode'] = True
    
    # 4. Create Outputs
    out_cols = [
        'event_id', 'centroid_lat', 'centroid_lon', 'first_detected', 'last_detected', 
        'observation_count', 'mean_frp', 'class', 'anomaly.score', 'blind_review_mode'
    ]
    candidates_out = candidates[out_cols].copy()
    candidates_out.to_csv('data/labels/ground_truth_candidates.csv', index=False)
    
    # Create verification manifest (summary of strata hits)
    strata_counts = {
        k: candidates[k].sum() for k in targets.keys()
    }
    with open('data/labels/verification_manifest.json', 'w') as f:
        json.dump({
            "total_candidates": len(candidates),
            "blind_review_count": int(candidates['blind_review_mode'].sum()),
            "strata_representation": {k: int(v) for k, v in strata_counts.items()}
        }, f, indent=4)
        
    print(f"Sampled {len(candidates)} verification candidates.")
    for k, v in strata_counts.items():
        print(f" - {k}: {v}")

if __name__ == "__main__":
    run_sampling()
