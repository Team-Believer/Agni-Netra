import numpy as np
import pandas as pd
import os
import json
import uuid

class SyntheticEventGenerator:
    def __init__(self, seed=42, generator_id="A"):
        self.seed = seed
        np.random.seed(seed)
        self.generator_id = generator_id
        
        self.classes = [
            'Industrial Fire', 
            'Routine Flare / Persistent Industrial Heat', 
            'Wildfire', 
            'Agricultural Burn', 
            'Other Thermal Source', 
            'Unknown'
        ]
        
        self.environments = [
            'dense industrial/urban',
            'mixed industrial-residential',
            'agricultural',
            'forest/wildland',
            'mixed rural-industrial',
            'coastal/heterogeneous',
            'sparsely developed regions'
        ]
        
        # Generator A vs B parameter shifts
        self.noise_multiplier = 1.0 if generator_id == "A" else 1.5
        self.env_shift = 0.0 if generator_id == "A" else 0.2
        
    def _sample_latent(self, event_class, environment):
        """Generates latent parameters with deliberate overlap across classes."""
        latent = {
            'thermal_intensity_mu': 0,
            'temporal_persistence_mu': 0,
            'day_night_bias': 0, # -1 day, 1 night, 0 balanced
            'vegetation_proxy': 0,
            'industrial_proxy': 0
        }
        
        # Environmental Base
        if 'industrial' in environment or 'urban' in environment:
            latent['industrial_proxy'] = np.random.uniform(0.6, 1.0)
            latent['vegetation_proxy'] = np.random.uniform(0.0, 0.4)
        elif 'forest' in environment or 'agricultural' in environment:
            latent['industrial_proxy'] = np.random.uniform(0.0, 0.4)
            latent['vegetation_proxy'] = np.random.uniform(0.6, 1.0)
        else:
            latent['industrial_proxy'] = np.random.uniform(0.3, 0.7)
            latent['vegetation_proxy'] = np.random.uniform(0.3, 0.7)
            
        # Add Generator Shift to Environment Latents
        latent['industrial_proxy'] = np.clip(latent['industrial_proxy'] + np.random.randn()*self.env_shift, 0, 1)
        
        # Class Overlays (highly overlapping)
        if event_class == 'Industrial Fire':
            latent['thermal_intensity_mu'] = np.random.normal(50, 20)
            latent['temporal_persistence_mu'] = np.random.normal(24, 12)
            latent['industrial_proxy'] = np.clip(latent['industrial_proxy'] + 0.2, 0, 1)
        elif event_class == 'Routine Flare / Persistent Industrial Heat':
            latent['thermal_intensity_mu'] = np.random.normal(30, 15)
            latent['temporal_persistence_mu'] = np.random.normal(720, 200) # highly persistent
            latent['industrial_proxy'] = np.clip(latent['industrial_proxy'] + 0.3, 0, 1)
        elif event_class == 'Wildfire':
            latent['thermal_intensity_mu'] = np.random.normal(80, 40)
            latent['temporal_persistence_mu'] = np.random.normal(48, 24)
            latent['day_night_bias'] = -0.3 # slightly more day detections
            latent['vegetation_proxy'] = np.clip(latent['vegetation_proxy'] + 0.4, 0, 1)
        elif event_class == 'Agricultural Burn':
            latent['thermal_intensity_mu'] = np.random.normal(15, 5)
            latent['temporal_persistence_mu'] = np.random.normal(6, 3)
            latent['day_night_bias'] = -0.6
            latent['vegetation_proxy'] = np.clip(latent['vegetation_proxy'] + 0.3, 0, 1)
        elif event_class == 'Other Thermal Source':
            latent['thermal_intensity_mu'] = np.random.normal(40, 30)
            latent['temporal_persistence_mu'] = np.random.normal(48, 48)
        else: # Unknown
            latent['thermal_intensity_mu'] = np.random.uniform(5, 100)
            latent['temporal_persistence_mu'] = np.random.uniform(1, 100)
            
        # Ensure positivity
        latent['thermal_intensity_mu'] = max(2.0, latent['thermal_intensity_mu'])
        latent['temporal_persistence_mu'] = max(1.0, latent['temporal_persistence_mu'])
        return latent

    def _generate_features_from_latent(self, latent, event_id, event_class, env, is_hard_case=None):
        """Generates observed noisy features from latent properties. No direct class lookup here!"""
        f = {'event_id': event_id, 'synthetic_environment': env, 'TRUE_SYNTHETIC_CLASS': event_class}
        
        # --- HARD CASES INJECTION ---
        if is_hard_case == "flare_spike":
            latent['thermal_intensity_mu'] *= 5.0
        elif is_hard_case == "wildfire_factory":
            latent['industrial_proxy'] = 0.9
            latent['vegetation_proxy'] = 0.9
        elif is_hard_case == "ag_near_industrial":
            latent['industrial_proxy'] = 0.8
        elif is_hard_case == "cloud_obscured":
            latent['thermal_intensity_mu'] *= 0.2
            
        # --- THERMAL FEATURES ---
        # Introduce measurement noise
        noise_factor = np.random.uniform(0.1, 0.4) * self.noise_multiplier
        f['final_max_frp'] = np.random.normal(latent['thermal_intensity_mu'], latent['thermal_intensity_mu'] * noise_factor)
        f['final_max_frp'] = max(1.0, f['final_max_frp'])
        
        # Online features (e.g., current is usually lower or equal to final)
        f['current_max_frp'] = f['final_max_frp'] * np.random.uniform(0.6, 1.0)
        
        f['final_duration'] = np.random.normal(latent['temporal_persistence_mu'], latent['temporal_persistence_mu'] * noise_factor)
        f['final_duration'] = max(1.0, f['final_duration'])
        
        f['current_duration'] = f['final_duration'] * np.random.uniform(0.1, 0.9)
        
        f['final_observation_count'] = max(1, int(f['final_duration'] / np.random.uniform(4, 12)))
        f['observation_count_so_far'] = max(1, int(f['final_observation_count'] * np.random.uniform(0.1, 0.9)))
        
        f['FRP_baseline'] = max(0, f['final_max_frp'] * np.random.normal(0.5, 0.2))
        f['FRP_variability'] = f['final_max_frp'] * np.random.uniform(0.1, 0.5)
        
        # BEHAVIOR
        f['anomaly.score'] = np.clip(np.random.normal((f['current_max_frp'] - f['FRP_baseline']) / max(f['FRP_baseline'], 1), 1.0), 0, 10)
        
        # PROXY CONTEXT
        f['proxy_industrial_context'] = np.clip(np.random.normal(latent['industrial_proxy'], 0.1 * self.noise_multiplier), 0, 1)
        f['proxy_vegetation_context'] = np.clip(np.random.normal(latent['vegetation_proxy'], 0.1 * self.noise_multiplier), 0, 1)
        
        # GEOLOCATION
        f['geolocation_error_m'] = np.random.exponential(100 * self.noise_multiplier)
        # Lat/Lon are purely random bounds to avoid spatial leakage
        f['centroid_lat'] = np.random.uniform(-90, 90)
        f['centroid_lon'] = np.random.uniform(-180, 180)
        
        # --- SENTINEL-2 FEATURES ---
        f['time_delta_hours'] = np.random.normal(0, 120)
        f['cloud_fraction'] = np.clip(np.random.normal(0.3, 0.3), 0, 1)
        if is_hard_case == "cloud_obscured":
            f['cloud_fraction'] = 0.99
            
        f['sentinel_available'] = np.random.rand() > 0.1 # 10% completely missing
        if is_hard_case == "sentinel_missing":
            f['sentinel_available'] = False
            
        # Generate B04 (Red), B08 (NIR), B12 (SWIR)
        base_swir = latent['thermal_intensity_mu'] / 100.0
        b12 = np.clip(np.random.normal(base_swir + latent['industrial_proxy']*0.2, 0.1), 0, 1)
        b08 = np.clip(np.random.normal(latent['vegetation_proxy']*0.8, 0.1), 0, 1)
        b04 = np.clip(np.random.normal(0.2, 0.1), 0, 1)
        
        ndvi = (b08 - b04) / max((b08 + b04), 0.01)
        
        if f['sentinel_available'] and f['cloud_fraction'] < 0.8:
            f['S2_B12'] = b12
            f['S2_B08'] = b08
            f['S2_B04'] = b04
            f['S2_NDVI'] = ndvi
        else:
            f['S2_B12'] = np.nan
            f['S2_B08'] = np.nan
            f['S2_B04'] = np.nan
            f['S2_NDVI'] = np.nan
            
        f['S2_B12_online'] = f['S2_B12'] if f['time_delta_hours'] <= 0 else np.nan
        f['S2_B08_online'] = f['S2_B08'] if f['time_delta_hours'] <= 0 else np.nan
        f['S2_B04_online'] = f['S2_B04'] if f['time_delta_hours'] <= 0 else np.nan
        f['S2_NDVI_online'] = f['S2_NDVI'] if f['time_delta_hours'] <= 0 else np.nan
        
        # --- GENERATOR TRACE ---
        f['latent_source_type'] = event_class # FORBIDDEN FEATURE
        f['generation_rule_id'] = self.generator_id # FORBIDDEN FEATURE
        
        return f

    def generate_dataset(self, n_events=75000):
        records = []
        
        class_probs = [0.15, 0.15, 0.20, 0.20, 0.15, 0.15]
        env_probs = [1/7]*7
        
        # Standard Generation
        for i in range(n_events):
            c = np.random.choice(self.classes, p=class_probs)
            e = np.random.choice(self.environments, p=env_probs)
            latent = self._sample_latent(c, e)
            f = self._generate_features_from_latent(latent, f"SYN-{self.generator_id}-{i}", c, e)
            records.append(f)
            
        # Hard Cases injection
        hard_cases = [
            ("Routine Flare / Persistent Industrial Heat", "flare_spike"),
            ("Industrial Fire", "cloud_obscured"),
            ("Wildfire", "wildfire_factory"),
            ("Agricultural Burn", "ag_near_industrial"),
            ("Industrial Fire", "sentinel_missing")
        ]
        
        for idx, (hc_class, hc_name) in enumerate(hard_cases):
            for i in range(100): # 100 of each hard case
                latent = self._sample_latent(hc_class, self.environments[0])
                f = self._generate_features_from_latent(latent, f"SYN-HC-{self.generator_id}-{idx}-{i}", hc_class, self.environments[0], is_hard_case=hc_name)
                records.append(f)
                
        df = pd.DataFrame(records)
        return df
        
def generate_synthetic_framework():
    os.makedirs('data/synthetic', exist_ok=True)
    
    gen_a = SyntheticEventGenerator(seed=42, generator_id="A")
    df_a = gen_a.generate_dataset(n_events=60000) # Train/Val predominantly A
    
    gen_b = SyntheticEventGenerator(seed=999, generator_id="B")
    df_b = gen_b.generate_dataset(n_events=15000) # Generator Shift test
    
    full_df = pd.concat([df_a, df_b], ignore_index=True)
    
    # Generate Synthetic Weak Labels with 20% noise
    np.random.seed(42)
    def add_noise(c):
        if np.random.rand() < 0.20:
            return np.random.choice(gen_a.classes)
        return c
    full_df['SIMULATED_WEAK_LABEL_20'] = full_df['TRUE_SYNTHETIC_CLASS'].apply(add_noise)
    
    def add_noise_40(c):
        if np.random.rand() < 0.40:
            return np.random.choice(gen_a.classes)
        return c
    full_df['SIMULATED_WEAK_LABEL_40'] = full_df['TRUE_SYNTHETIC_CLASS'].apply(add_noise_40)
    
    full_df.to_csv('data/synthetic/synthetic_ground_truth.csv', index=False)
    
    print(f"Generated {len(full_df)} synthetic events.")

if __name__ == "__main__":
    generate_synthetic_framework()
