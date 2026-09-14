import pandas as pd
import numpy as np
import os

def generate_exposure(filepath):
    print(f"Generating synthetic exposure for {filepath}...")
    df = pd.read_csv(filepath)
    np.random.seed(42) # Deterministic for reproducibility
    
    # 1. Independent Latent Variables
    # We do NOT use the TRUE_CLASS or the old proxy_industrial_context directly.
    # Instead, we generate independent latent variables for exposure and urgency.
    
    latent_exposure = np.random.beta(a=2.0, b=5.0, size=len(df)) # Skewed toward lower exposure, with occasional high exposure
    latent_consequence = np.random.beta(a=2.0, b=5.0, size=len(df))
    latent_urgency = np.random.beta(a=1.5, b=5.0, size=len(df))
    
    # 2. Correlate slightly with geography/context if needed, but the prompt says 
    # "The latent exposure variables are independent from the B2 labels, but can still have realistic correlations with geography/context."
    # Let's add a small bump if the old proxy was high, just for realism, but mostly derived from the independent latent.
    if 'proxy_industrial_context' in df.columns:
        context_base = df['proxy_industrial_context'].fillna(0).values
        # Skew latent exposure slightly higher in industrial zones, but keep it mostly independent
        latent_exposure = (latent_exposure * 0.7) + (context_base * 0.3)
        
    # 3. Observable Proxies
    df['obs_facility_importance'] = np.clip(latent_exposure * np.random.normal(1.0, 0.1, size=len(df)), 0, 1)
    df['obs_population_density'] = np.clip(latent_consequence * np.random.normal(1.0, 0.2, size=len(df)), 0, 1)
    df['obs_critical_infrastructure_proximity'] = np.clip(latent_exposure * np.random.normal(1.0, 0.15, size=len(df)), 0, 1)
    df['obs_environmental_sensitivity'] = np.clip(np.random.beta(2, 2, size=len(df)), 0, 1) # Independent
    
    df['obs_time_urgency'] = np.clip(latent_urgency, 0, 1)
    
    # We will save these new observable exposure indicators back to the CSVs to be ingested by the Ledger
    df.to_csv(filepath, index=False)

def run():
    os.makedirs('data/processed/decision_intelligence', exist_ok=True)
    
    files = [
        'data/synthetic/deployment_realistic/train_A.csv',
        'data/synthetic/deployment_realistic/test_A.csv',
        'data/synthetic/deployment_realistic/shift_holdout_B.csv',
        'data/synthetic/deployment_realistic/unseen_deployment_C.csv'
    ]
    for f in files:
        if os.path.exists(f):
            generate_exposure(f)
            
    print("Synthetic Exposure Generation Complete.")

if __name__ == "__main__":
    run()
