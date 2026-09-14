import pandas as pd
import numpy as np
import os

def split_scenarios():
    os.makedirs('data/processed/b2_synthetic', exist_ok=True)
    
    # Load 
    df = pd.read_csv('data/synthetic/synthetic_ground_truth.csv')
    
    # Split Generator A vs Generator B for testing generator shift generalization
    # Generator A is Train/Val/Test. Generator B is purely Holdout
    gen_a_mask = df['generation_rule_id'] == 'A'
    df_a = df[gen_a_mask].copy()
    df_b = df[~gen_a_mask].copy()
    
    # Stratified Split for A
    # Using simple temporal splitting logic simulation by ID (since we don't have explicit date ranges in the generator currently)
    # 70% Train, 15% Val, 15% Test
    n = len(df_a)
    train_end = int(n * 0.70)
    val_end = int(n * 0.85)
    
    train_df = df_a.iloc[:train_end]
    val_df = df_a.iloc[train_end:val_end]
    test_df = df_a.iloc[val_end:]
    
    # Distribution Shift Holdout
    # E.g., test only on high cloud fraction events from Generator A
    dist_shift_df = test_df[test_df['cloud_fraction'] > 0.6]
    
    train_df.to_csv('data/processed/b2_synthetic/train.csv', index=False)
    val_df.to_csv('data/processed/b2_synthetic/validation.csv', index=False)
    test_df.to_csv('data/processed/b2_synthetic/test.csv', index=False)
    dist_shift_df.to_csv('data/processed/b2_synthetic/distribution_shift.csv', index=False)
    df_b.to_csv('data/processed/b2_synthetic/generator_shift.csv', index=False)
    
    print("Splits generated successfully.")
    
if __name__ == "__main__":
    split_scenarios()
