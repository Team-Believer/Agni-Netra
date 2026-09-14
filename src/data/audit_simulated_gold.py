import pandas as pd
import numpy as np
import os
import json
from sklearn.metrics import cohen_kappa_score, f1_score, confusion_matrix

def audit_simulated_gold():
    print("Running Simulated Gold Quality & Agreement Audit...")
    
    # Load data
    gt_df = pd.read_csv('data/synthetic/synthetic_ground_truth.csv')
    labels_df = pd.read_csv('data/synthetic/simulated_expert_labels.csv')
    reviews_df = pd.read_csv('data/synthetic/simulated_expert_reviews.csv')
    
    df = pd.merge(labels_df, gt_df[['event_id', 'TRUE_SYNTHETIC_CLASS']], on='event_id')
    
    report = {}
    
    # 1. Consensus Breakdown
    report['simulated_gold_count'] = len(df[df['label_tier'] == 'SIMULATED_GOLD'])
    report['simulated_silver_count'] = len(df[df['label_tier'] == 'SIMULATED_SILVER'])
    report['simulated_disputed_count'] = len(df[df['label_tier'] == 'SIMULATED_DISPUTED'])
    report['simulated_unknown_count'] = len(df[df['label_tier'] == 'SIMULATED_UNKNOWN'])
    
    # 2. Quality Audit against TRUE_SYNTHETIC_CLASS
    # We only measure this on events that received a definitive label (Gold or Silver)
    definitive_df = df[df['simulated_verified_class'] != 'Unknown'].copy()
    if len(definitive_df) > 0:
        f1 = f1_score(definitive_df['TRUE_SYNTHETIC_CLASS'], definitive_df['simulated_verified_class'], average='macro')
        report['macro_f1_vs_true_synthetic'] = float(f1)
    else:
        report['macro_f1_vs_true_synthetic'] = 0.0
        
    # 3. Inter-Rater Agreement (Cohen's Kappa on BLIND mode)
    blind_reviews = reviews_df[reviews_df['review_mode'] == 'BLIND']
    rev_a = blind_reviews[blind_reviews['reviewer_id'] == 'REVIEWER_A_CONSERVATIVE']['class_guess'].values
    rev_b = blind_reviews[blind_reviews['reviewer_id'] == 'REVIEWER_B_BALANCED']['class_guess'].values
    rev_c = blind_reviews[blind_reviews['reviewer_id'] == 'REVIEWER_C_SENSITIVE']['class_guess'].values
    
    if len(rev_a) > 0 and len(rev_a) == len(rev_b):
        kappa_ab = cohen_kappa_score(rev_a, rev_b)
        report['cohen_kappa_A_vs_B'] = float(kappa_ab)
        
    # 4. Model Assistance Bias
    assisted_reviews = reviews_df[reviews_df['review_mode'] == 'MODEL_ASSISTED']
    if len(assisted_reviews) > 0:
        a_assist = assisted_reviews[assisted_reviews['reviewer_id'] == 'REVIEWER_A_CONSERVATIVE']['class_guess'].values
        # How often did the blind reviewer change their mind when shown the model?
        changed_mind_count = np.sum(rev_a != a_assist)
        report['reviewer_A_changed_mind_rate'] = float(changed_mind_count / len(rev_a))
        
    # 5. REAL GOLD FIREWALL AUDIT
    real_gold_count = 0
    if os.path.exists('data/labels/verified_events.csv'):
        real_verified = pd.read_csv('data/labels/verified_events.csv')
        real_gold_count = len(real_verified[real_verified['label_tier'] == 'GOLD'])
        
    report['real_gold_firewall_status'] = "PASS" if real_gold_count == 0 else "FAIL"
    assert real_gold_count == 0, "REAL GOLD FIREWALL BREACHED!"
    
    assert len(df[df['label_tier'] == 'GOLD']) == 0, "SIMULATED PIPELINE PRODUCED REAL GOLD!"
    
    with open('data/synthetic/simulated_review_manifest.json', 'w') as f:
        json.dump(report, f, indent=4)
        
    print(json.dumps(report, indent=4))
    print("Audit Complete.")

if __name__ == "__main__":
    audit_simulated_gold()
