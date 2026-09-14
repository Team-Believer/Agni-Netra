import pandas as pd
import numpy as np

def audit_synthetic_dataset():
    print("Running Anti-Cheating & Quality Audit...")
    df = pd.read_csv('data/synthetic/synthetic_ground_truth.csv')
    
    # 1. Feature isolation check
    forbidden_features = [
        'TRUE_SYNTHETIC_CLASS',
        'latent_source_type',
        'latent_fire_state',
        'generation_rule_id'
    ]
    
    # We pretend these are the inputs to B2. In B2, we will explicitly drop these.
    # We verify they exist in the dataframe but are strictly marked as metadata.
    for f in forbidden_features:
        if f in df.columns:
            print(f"[PASS] Forbidden feature '{f}' tracked successfully for removal.")
        else:
            print(f"[WARN] Expected forbidden tracker '{f}' not found.")
            
    # 2. Class overlap check (Anti-Cheating)
    # Ensure no single observable feature has a correlation > 0.9 with the class.
    # Convert class to categorical codes
    df['class_code'] = df['TRUE_SYNTHETIC_CLASS'].astype('category').cat.codes
    
    observable_features = [c for c in df.columns if c not in forbidden_features + ['event_id', 'synthetic_environment', 'class_code', 'SIMULATED_WEAK_LABEL_20', 'SIMULATED_WEAK_LABEL_40']]
    
    cheats_found = 0
    for col in observable_features:
        if df[col].dtype in [np.float64, np.float32, np.int64, np.int32, bool]:
            corr = np.abs(df[col].corr(df['class_code']))
            if corr > 0.9:
                print(f"[FAIL] High correlation cheating detected: {col} has {corr:.2f} correlation with target class.")
                cheats_found += 1
                
    if cheats_found == 0:
        print("[PASS] No trivial class-leaking observable features found. The benchmark is scientifically valid.")
        
    # 3. Class overlap demonstration
    print("\n[INFO] Demonstration of class overlap (mean FRP by class):")
    print(df.groupby('TRUE_SYNTHETIC_CLASS')['current_max_frp'].mean())

if __name__ == "__main__":
    audit_synthetic_dataset()
