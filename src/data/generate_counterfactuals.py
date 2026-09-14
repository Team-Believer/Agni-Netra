import pandas as pd
import numpy as np
import os
from generate_synthetic_ground_truth import SyntheticEventGenerator

def generate_counterfactuals():
    gen = SyntheticEventGenerator(seed=777, generator_id="A")
    records = []
    
    # We will generate 500 pairs (1000 events)
    # Pair A: same thermal signal, different context
    for i in range(100):
        c = "Industrial Fire"
        e1 = "dense industrial/urban"
        e2 = "forest/wildland"
        
        # Base Latent
        latent1 = gen._sample_latent(c, e1)
        # Counterfactual Latent (change environment proxies)
        latent2 = latent1.copy()
        latent2['industrial_proxy'] = np.random.uniform(0.0, 0.4)
        latent2['vegetation_proxy'] = np.random.uniform(0.6, 1.0)
        
        # We ensure random states are identical for the noise generation to isolate the effect
        state = np.random.get_state()
        f1 = gen._generate_features_from_latent(latent1, f"CF-PairA-{i}-1", c, e1)
        np.random.set_state(state)
        f2 = gen._generate_features_from_latent(latent2, f"CF-PairA-{i}-2", c, e2)
        
        f1['counterfactual_pair_id'] = f"CF-PairA-{i}"
        f2['counterfactual_pair_id'] = f"CF-PairA-{i}"
        
        records.append(f1)
        records.append(f2)
        
    df = pd.DataFrame(records)
    df.to_csv('data/synthetic/synthetic_counterfactuals.csv', index=False)
    print(f"Generated {len(df)} counterfactual events.")

if __name__ == "__main__":
    generate_counterfactuals()
