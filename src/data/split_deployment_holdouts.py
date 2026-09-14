import pandas as pd
import numpy as np
import os

def split_holdouts():
    print("Splitting Deployment Holdouts...")
    df = pd.read_csv('data/synthetic/deployment_realistic/deployment_simulation.csv')
    
    # Generator Splits
    df_a = df[df['generator_id'] == 'A'].copy()
    df_b = df[df['generator_id'] == 'B'].copy()
    df_c = df[df['generator_id'] == 'C'].copy()
    
    # Facility-level grouped holdout for Generator A
    # We want 80% facilities for training, 20% for testing
    facilities = df_a['synthetic_facility_id'].unique()
    np.random.shuffle(facilities)
    
    split_idx = int(len(facilities) * 0.8)
    train_facs = set(facilities[:split_idx])
    
    df_train = df_a[df_a['synthetic_facility_id'].isin(train_facs)].copy()
    df_test_a = df_a[~df_a['synthetic_facility_id'].isin(train_facs)].copy()
    
    # Save splits
    df_train.to_csv('data/synthetic/deployment_realistic/train_A.csv', index=False)
    df_test_a.to_csv('data/synthetic/deployment_realistic/test_A.csv', index=False)
    df_b.to_csv('data/synthetic/deployment_realistic/shift_holdout_B.csv', index=False)
    df_c.to_csv('data/synthetic/deployment_realistic/unseen_deployment_C.csv', index=False)
    
    print(f"Splits complete. Train A: {len(df_train)}, Test A: {len(df_test_a)}, Shift B: {len(df_b)}, Unseen C: {len(df_c)}")

if __name__ == "__main__":
    split_holdouts()
