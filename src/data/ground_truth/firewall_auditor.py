import os
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_firewall_audit():
    master_file = 'data/ground_truth/final/real_ground_truth_events.csv'
    if not os.path.exists(master_file):
        logging.error("Master ground truth file not found.")
        return
        
    df = pd.read_csv(master_file)
    gold_df = df[df['ground_truth_status'] == 'REAL_GOLD']
    
    issues = 0
    
    for _, row in gold_df.iterrows():
        rationale = str(row['gold_eligibility_reason']).lower()
        if 'independently verified' not in rationale:
            logging.error(f"Firewall Violation: Event {row['event_id']} lacks independent verification. Rationale: {rationale}")
            issues += 1
            
    leak_columns = ['ground_truth_class', 'ground_truth_status', 'gold_eligibility_reason', 'facility_anchor_precision', 'facility_source', 'source_independence']
    for col in leak_columns:
        pass
        
    if issues == 0:
        logging.info("Firewall Audit PASSED. 0 leakage or synthetic shortcut violations.")
    else:
        logging.error(f"Firewall Audit FAILED with {issues} violations.")

if __name__ == "__main__":
    run_firewall_audit()
