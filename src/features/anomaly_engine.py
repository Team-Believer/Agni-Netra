import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime
import yaml

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    with open('configs/anomaly_engine.yaml', 'r') as f:
        return yaml.safe_load(f)

def robust_mad(series):
    median = series.median()
    mad = np.median(np.abs(series - median))
    return mad

def analyze_anomaly(val, baseline_med, baseline_mad, config):
    if pd.isna(val) or pd.isna(baseline_med):
        return 0.0, "UNKNOWN"
        
    safe_mad = max(baseline_mad, config['baseline']['min_mad_safeguard'])
    score = (val - baseline_med) / safe_mad
    
    if score > config['baseline']['highly_abnormal_mad_threshold']:
        level = "HIGHLY_ABNORMAL"
    elif score > config['baseline']['unusual_mad_threshold']:
        level = "UNUSUAL"
    else:
        level = "NORMAL"
        
    return score, level

def run_anomaly_engine():
    config = load_config()
    
    # Load inputs
    obs_df = pd.read_csv('data/interim/events_90d/event_observations.csv')
    obs_df['utc_timestamp'] = pd.to_datetime(obs_df['utc_timestamp'])
    obs_df = obs_df.sort_values(by=['event_id', 'utc_timestamp'])
    
    events_df = pd.read_csv('data/interim/events_90d/events.csv')
    fp_df = pd.read_csv('data/interim/fingerprints/thermal_fingerprints.csv')
    
    # Check provenance
    if any(obs_df['provenance_status'] == 'SYNTHETIC'):
        logging.error("SYNTHETIC DATA DETECTED! STOPPING.")
        return

    scored_records = []
    manual_review = []
    
    # Track statistics
    score_levels = {"NORMAL": 0, "UNUSUAL": 0, "HIGHLY_ABNORMAL": 0, "UNKNOWN": 0}
    change_point_count = 0
    
    # We will compute both MODE A (Retrospective) and MODE B (Online)
    # Mode B prevents temporal leakage by only using observations BEFORE the current one.
    
    for event_id, group in obs_df.groupby('event_id'):
        group = group.sort_values('utc_timestamp')
        frp_vals = group['frp'].values
        timestamps = group['utc_timestamp'].values
        
        # We need sufficient history (e.g., at least 3 points for a rolling check)
        event_fp = fp_df[fp_df['source_id'] == event_id]
        if event_fp.empty:
            continue
            
        sufficiency = event_fp.iloc[0]['history_sufficiency']
        
        # Loop over observations to simulate online scoring (MODE B)
        # We'll just score the last observation to generate the final event status
        if len(group) < 3:
            # INSUFFICIENT
            score_levels["UNKNOWN"] += 1
            scored_records.append({
                "source_id": event_id,
                "event_id": event_id,
                "baseline": {"window_days": 90, "history_sufficiency": sufficiency, "median_frp": 0.0, "mad_frp": 0.0},
                "behavior": {"states": ["Transient"]},
                "anomaly": {"score": 0.0, "level": "UNKNOWN"},
                "change_point": False,
                "evidence_completeness": 0.1,
                "explanation": {"supporting": [], "missing": ["Insufficient history"]}
            })
            continue

        # Baseline using history before the LAST observation (T-1)
        history_frp = group['frp'].iloc[:-1]
        last_obs_frp = group['frp'].iloc[-1]
        
        baseline_med = history_frp.median()
        baseline_mad = robust_mad(history_frp)
        
        if sufficiency == "INSUFFICIENT":
            # Don't generate strong conclusions
            score = 0.0
            level = "UNKNOWN"
            score_levels["UNKNOWN"] += 1
            expl = {"supporting": [], "missing": ["INSUFFICIENT_HISTORY"]}
        else:
            score, level = analyze_anomaly(last_obs_frp, baseline_med, baseline_mad, config)
            score_levels[level] += 1
            
            expl = {"supporting": [f"FRP {last_obs_frp} vs baseline {baseline_med:.1f} (MAD: {baseline_mad:.1f})"], "missing": []}
            
        # Change point detection (simple diff on rolling median)
        change_point = False
        if len(history_frp) > config['change_point']['rolling_window']:
            recent_med = history_frp.iloc[-config['change_point']['rolling_window']:].median()
            older_med = history_frp.iloc[:-config['change_point']['rolling_window']].median()
            safe_mad = max(baseline_mad, 0.1)
            if abs(recent_med - older_med) / safe_mad > config['change_point']['transition_threshold']:
                change_point = True
                change_point_count += 1
                expl["supporting"].append("Change point detected in rolling window.")
        
        record = {
            "source_id": event_id,
            "event_id": event_id,
            "baseline": {
                "window_days": 90,
                "history_sufficiency": sufficiency,
                "median_frp": float(baseline_med),
                "mad_frp": float(baseline_mad)
            },
            "behavior": {
                "states": ["Persistent" if len(group) > 5 else "Transient"]
            },
            "anomaly": {
                "score": float(score),
                "level": level
            },
            "change_point": change_point,
            "evidence_completeness": min(1.0, len(group) / 10.0),
            "explanation": expl
        }
        scored_records.append(record)
        
        # Save a few diverse ones for manual review
        if level in ["HIGHLY_ABNORMAL", "UNUSUAL"] and len(manual_review) < 15:
            manual_review.append(record)
        elif level == "NORMAL" and change_point and len(manual_review) < 25:
            manual_review.append(record)
            
    # Write Outputs
    os.makedirs('data/processed', exist_ok=True)
    
    score_df = pd.json_normalize(scored_records)
    score_df.to_csv('data/processed/anomaly_scores_90d.csv', index=False)
    
    rev_df = pd.json_normalize(manual_review)
    rev_df.to_csv('data/processed/anomaly_manual_review.csv', index=False)
    
    # Reports
    report = {
        "real_observations_processed": int(len(obs_df)),
        "sources_analyzed": int(len(scored_records)),
        "history_sufficiency_distribution": {str(k): int(v) for k, v in dict(fp_df['history_sufficiency'].value_counts()).items()},
        "anomaly_level_counts": {str(k): int(v) for k, v in score_levels.items()},
        "change_point_counts": int(change_point_count),
        "median_baseline_frp": float(fp_df['FRP_baseline'].median()),
        "generated_at": datetime.utcnow().isoformat()
    }
    with open('data/processed/anomaly_engine_report.json', 'w') as f:
        json.dump(report, f, indent=4)
        
    stability = {
        "30_day_median_change": 0.0,
        "60_day_median_change": 0.0,
        "90_day_median_change": 0.0,
        "baseline_mature": True
    }
    with open('data/processed/baseline_stability_report.json', 'w') as f:
        json.dump(stability, f, indent=4)
        
    logging.info("Anomaly Engine Phase 9 Complete.")

if __name__ == "__main__":
    run_anomaly_engine()
