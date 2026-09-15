import os
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_splits():
    events_file = 'data/ground_truth/final/real_ground_truth_events.csv'
    out_dir = 'data/ground_truth/splits'
    os.makedirs(out_dir, exist_ok=True)
    
    if not os.path.exists(events_file):
        logging.error("Final events file missing.")
        return
        
    df = pd.read_csv(events_file)
    
    # Split by event ID. We put all Gold and Silver in TEST.
    # The rest we can split 80/10/10 temporally.
    
    gold_silver = df[df['ground_truth_status'].isin(['REAL_GOLD', 'REAL_SILVER'])]
    unknowns = df[~df['ground_truth_status'].isin(['REAL_GOLD', 'REAL_SILVER'])]
    
    # Sort unknowns temporally for holdout
    unknowns = unknowns.sort_values(by='start_time')
    n = len(unknowns)
    
    train_n = int(n * 0.8)
    val_n = int(n * 0.1)
    
    train_set = unknowns.iloc[:train_n]
    val_set = unknowns.iloc[train_n:train_n+val_n]
    test_set_unknowns = unknowns.iloc[train_n+val_n:]
    
    test_set = pd.concat([gold_silver, test_set_unknowns])
    
    train_set[['event_id']].to_csv(f"{out_dir}/train_event_ids.csv", index=False)
    val_set[['event_id']].to_csv(f"{out_dir}/validation_event_ids.csv", index=False)
    test_set[['event_id']].to_csv(f"{out_dir}/test_event_ids.csv", index=False)
    
    logging.info(f"Created clean splits. Train: {len(train_set)}, Val: {len(val_set)}, Test: {len(test_set)} (including {len(gold_silver)} verified).")

if __name__ == "__main__":
    create_splits()
