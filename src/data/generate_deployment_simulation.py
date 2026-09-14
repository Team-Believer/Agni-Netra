import pandas as pd
import numpy as np
import os
import json
import uuid
from scipy.stats import norm

class DeploymentSimGenerator:
    def __init__(self, profile_path, seed=42, generator_id="A"):
        self.seed = seed
        np.random.seed(seed)
        self.generator_id = generator_id
        
        with open(profile_path, 'r') as f:
            self.profile = json.load(f)
            
        self.classes = [
            'Industrial Fire', 'Routine Flare / Persistent Industrial Heat', 
            'Wildfire', 'Agricultural Burn', 'Other Thermal Source', 'Unknown'
        ]
        
        # Generator Variations
        self.noise_mult = 1.0
        self.class_probs = [0.15, 0.15, 0.20, 0.20, 0.15, 0.15]
        if generator_id == "B":
            self.noise_mult = 1.5
            self.class_probs = [0.10, 0.20, 0.25, 0.15, 0.10, 0.20] # Class imbalance
        elif generator_id == "C":
            self.noise_mult = 2.0
            self.class_probs = [0.05, 0.25, 0.10, 0.30, 0.10, 0.20] # Extreme shift
            
        # Pre-generate 1000 persistent facilities
        self.facilities = []
        for i in range(1000):
            fac = {
                'facility_id': f"FAC-{generator_id}-{i}",
                'fac_industrial_proxy': np.random.uniform(0.0, 1.0),
                'fac_vegetation_proxy': np.random.uniform(0.0, 1.0),
                'fac_lat': np.random.uniform(-90, 90),
                'fac_lon': np.random.uniform(-180, 180)
            }
            self.facilities.append(fac)

    def _inverse_transform_sample(self, quantiles, size=1):
        """Samples from the empirical marginal distribution using piecewise linear interpolation of quantiles."""
        q_points = np.linspace(0, 1, 11)
        u = np.random.uniform(0, 1, size)
        samples = np.interp(u, q_points, quantiles)
        return samples[0] if size == 1 else samples
        
    def _generate_trajectory(self, event_class, facility):
        """Generates the LATENT event trajectory from real-data marginals and reconstructs rank dependence."""
        
        # We enforce correlation structure using a Gaussian Copula approach
        # Target correlation between mean_frp (0), duration (1), and obs_count (2)
        # We approximate the spearman rank from the real profile
        
        cov = np.array([
            [1.0, 0.4, 0.6],
            [0.4, 1.0, 0.8],
            [0.6, 0.8, 1.0]
        ])
        
        # Cholesky decomposition to induce correlation in normal samples
        L = np.linalg.cholesky(cov)
        z = np.random.normal(size=3)
        correlated_z = L.dot(z)
        
        # Transform back to uniform
        u = norm.cdf(correlated_z)
        
        # Inverse transform to empirical marginals
        q_points = np.linspace(0, 1, 11)
        final_frp = np.interp(u[0], q_points, self.profile['FRP_quantiles'])
        final_duration = np.interp(u[1], q_points, self.profile['duration_hours_quantiles'])
        final_obs_count = np.interp(u[2], q_points, self.profile['observation_count_quantiles'])
        
        # Class overlays (latent scaling to create class separation while preserving marginal scales)
        if event_class == 'Industrial Fire':
            final_frp *= 1.5
            final_duration *= 0.5
        elif event_class == 'Routine Flare / Persistent Industrial Heat':
            final_frp *= 0.8
            final_duration *= 3.0
        elif event_class == 'Wildfire':
            final_frp *= 3.0
        elif event_class == 'Agricultural Burn':
            final_frp *= 0.5
            final_duration *= 0.1
            
        final_frp = max(1.0, final_frp)
        final_duration = max(1.0, final_duration)
        final_obs_count = max(1, int(final_obs_count))
        
        # Base Sentinel
        missing_rate = self.profile['sentinel_missing_rate'] * self.noise_mult
        has_sentinel = np.random.rand() > missing_rate
        cloud_frac = np.clip(np.random.normal(0.3 * self.noise_mult, 0.3), 0, 1)
        
        ndvi = np.clip(np.random.normal(facility['fac_vegetation_proxy'], 0.2), 0, 1)
        
        return {
            'final_frp': final_frp,
            'final_duration': final_duration,
            'final_obs_count': final_obs_count,
            'has_sentinel': has_sentinel,
            'cloud_fraction': cloud_frac,
            'true_ndvi': ndvi
        }
        
    def _slice_snapshot(self, t_fraction, latent_traj):
        """Reveals only a prefix of the latent trajectory (Online snapshot simulation)"""
        return {
            'current_frp': latent_traj['final_frp'] * np.random.uniform(0.5, 1.0) * (t_fraction + 0.1),
            'current_duration': latent_traj['final_duration'] * t_fraction,
            'observation_count_so_far': max(1, int(latent_traj['final_obs_count'] * t_fraction))
        }

    def generate_events(self, n_events):
        records = []
        for i in range(n_events):
            c = np.random.choice(self.classes, p=self.class_probs)
            fac = np.random.choice(self.facilities)
            
            latent_traj = self._generate_trajectory(c, fac)
            
            # Generate T_snapshot (e.g. at 50% of event lifespan)
            t_fraction = np.random.uniform(0.1, 0.9)
            online_obs = self._slice_snapshot(t_fraction, latent_traj)
            
            f = {
                'event_id': f"DEP-{self.generator_id}-{i}",
                'synthetic_facility_id': fac['facility_id'],
                'generator_id': self.generator_id,
                'TRUE_DEPLOYMENT_SIM_CLASS': c,
                'proxy_industrial_context': fac['fac_industrial_proxy'],
                'proxy_vegetation_context': fac['fac_vegetation_proxy'],
                'centroid_lat': fac['fac_lat'] + np.random.normal(0, 0.01),
                'centroid_lon': fac['fac_lon'] + np.random.normal(0, 0.01),
                
                # Final features (Retrospective)
                'final_max_frp': latent_traj['final_frp'],
                'final_duration': latent_traj['final_duration'],
                'final_observation_count': latent_traj['final_obs_count'],
                
                # Online features (T_current)
                'current_max_frp': online_obs['current_frp'],
                'current_duration': online_obs['current_duration'],
                'observation_count_so_far': online_obs['observation_count_so_far'],
                
                # Sentinel (masked by clouds and availability)
                'S2_NDVI_online': latent_traj['true_ndvi'] if latent_traj['has_sentinel'] and latent_traj['cloud_fraction'] < 0.8 else np.nan
            }
            records.append(f)
            
        return pd.DataFrame(records)

def run():
    print("Generating Deployment-Realistic Simulation...")
    os.makedirs('data/synthetic/deployment_realistic', exist_ok=True)
    
    gen_a = DeploymentSimGenerator('data/processed/deployment_simulation/real_distribution_profile.json', seed=1, generator_id="A")
    df_a = gen_a.generate_events(60000)
    
    gen_b = DeploymentSimGenerator('data/processed/deployment_simulation/real_distribution_profile.json', seed=2, generator_id="B")
    df_b = gen_b.generate_events(10000)
    
    gen_c = DeploymentSimGenerator('data/processed/deployment_simulation/real_distribution_profile.json', seed=3, generator_id="C")
    df_c = gen_c.generate_events(5000) # Unseen final deployment test
    
    full_df = pd.concat([df_a, df_b, df_c], ignore_index=True)
    
    full_df.to_csv('data/synthetic/deployment_realistic/deployment_simulation.csv', index=False)
    print(f"Generated {len(full_df)} deployment events.")

if __name__ == "__main__":
    run()
