import pandas as pd
import numpy as np
import os
import json
from scipy.stats import ks_2samp

def audit_deployment():
    print("Running Deployment Similarity Audit...")
    
    with open('data/processed/deployment_simulation/real_distribution_profile.json', 'r') as f:
        real_profile = json.load(f)
        
    df = pd.read_csv('data/synthetic/deployment_realistic/deployment_simulation.csv')
    
    report = {}
    
    # 1. Similarity: Kolmogorov-Smirnov Test (Approximate via quantiles vs samples)
    # We use empirical quantiles for KS simulation
    real_frp_q = real_profile['FRP_quantiles']
    
    # Create a simulated real sample from quantiles for KS comparison
    u = np.random.uniform(0, 1, 10000)
    q_points = np.linspace(0, 1, 11)
    sim_real_frp = np.interp(u, q_points, real_frp_q)
    
    ks_stat, p_val = ks_2samp(df['final_max_frp'].dropna(), sim_real_frp)
    report['KS_statistic_FRP'] = float(ks_stat)
    
    # 2. Correlation Difference
    sim_corr = df[['final_max_frp', 'final_duration', 'final_observation_count']].corr(method='spearman')
    real_corr = real_profile['spearman_rank_correlation']
    
    corr_diff = abs(sim_corr.loc['final_max_frp', 'final_duration'] - real_corr['mean_frp']['duration_hours'])
    report['correlation_difference_FRP_duration'] = float(corr_diff)
    
    # 3. Sentinel Missingness Check
    report['synthetic_sentinel_missing_rate'] = float(df['S2_NDVI_online'].isna().mean())
    report['real_sentinel_missing_rate'] = real_profile['sentinel_missing_rate']
    
    # 4. REAL GOLD FIREWALL
    real_gold_count = 0
    if os.path.exists('data/labels/verified_events.csv'):
        real_verified = pd.read_csv('data/labels/verified_events.csv')
        real_gold_count = len(real_verified[real_verified['label_tier'] == 'GOLD'])
        
    report['real_gold_firewall_status'] = "PASS" if real_gold_count == 0 else "FAIL"
    assert real_gold_count == 0, "REAL GOLD FIREWALL BREACHED!"
    
    with open('data/processed/deployment_simulation/similarity_report.json', 'w') as f:
        json.dump(report, f, indent=4)
        
    print(json.dumps(report, indent=4))
    print("Audit Complete.")

if __name__ == "__main__":
    audit_deployment()
