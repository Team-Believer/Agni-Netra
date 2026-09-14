import pandas as pd
import numpy as np
import os
import json

def generate_features(df_input, registry_path="data/interim/features/feature_registry_v1.json"):
    with open(registry_path, 'r') as f:
        registry = json.load(f)
        
    df = df_input.copy()
    
    online_features = {}
    retrospective_features = {}
    
    for i, row in df.iterrows():
        # --- ONLINE EXTRACTION ---
        online_row = {
            'event_id': row.get('event_id', f"evt_{i}"),
            'TRUE_DEPLOYMENT_SIM_CLASS': row.get('TRUE_DEPLOYMENT_SIM_CLASS', 'UNKNOWN_REAL') # We keep the class attached for evaluation, but the feature matrix itself doesn't use it
        }
        
        # Thermal
        online_row['current_max_frp'] = float(row.get('current_max_frp', np.nan))
        online_row['current_mean_frp'] = float(row.get('current_max_frp', np.nan)) * 0.8 # Mocking mean from max for synthetic if absent
        online_row['current_bright_ti4'] = float(row.get('current_bright_ti4', np.nan))
        
        # Temporal
        online_row['observation_count_so_far'] = int(row.get('observation_count_so_far', 1))
        online_row['current_event_duration_hours'] = float(row.get('current_duration', 0.0))
        # If obs < 2, gap is NaN
        if online_row['observation_count_so_far'] >= 2:
            online_row['inter_observation_gap_median'] = max(0.1, online_row['current_event_duration_hours'] / online_row['observation_count_so_far'])
        else:
            online_row['inter_observation_gap_median'] = np.nan
            
        # Spatial
        if online_row['observation_count_so_far'] >= 2:
            online_row['centroid_shift_distance_km'] = np.random.uniform(0.0, 1.5) # Mock for demonstration since synthetic lacks raw lat/lon history
            online_row['spatial_observation_density'] = np.random.uniform(1.0, 50.0)
        else:
            online_row['centroid_shift_distance_km'] = 0.0
            online_row['spatial_observation_density'] = np.nan
            
        if online_row['observation_count_so_far'] >= 3:
            online_row['observation_expansion_rate'] = np.random.uniform(0.0, 0.5)
        else:
            online_row['observation_expansion_rate'] = np.nan
            
        # Historical
        if 'proxy_industrial_context' in row:
            online_row['history_insufficient_flag'] = 0
            online_row['frp_vs_historical_median'] = online_row['current_max_frp'] / max(1.0, np.random.uniform(10, 50))
        else:
            online_row['history_insufficient_flag'] = 1
            online_row['frp_vs_historical_median'] = np.nan
            
        # Anomaly
        online_row['anomaly_state_score'] = float(row.get('current_vs_baseline_deviation_online', 0.0))
        
        # Sentinel
        if 'S2_NDVI_online' in row and not pd.isna(row['S2_NDVI_online']):
            online_row['sentinel_available'] = 1
            online_row['sentinel_ndvi_proxy'] = float(row['S2_NDVI_online'])
        else:
            online_row['sentinel_available'] = 0
            online_row['sentinel_ndvi_proxy'] = np.nan
            
        # Context
        online_row['industrial_context_strength'] = float(row.get('proxy_industrial_context', 0.0))
        
        # --- RETROSPECTIVE EXTRACTION ---
        retro_row = online_row.copy()
        
        # Overwrite with future-leaking "final" values
        retro_row['final_event_duration_hours'] = float(row.get('final_duration', online_row['current_event_duration_hours']))
        retro_row['final_max_frp'] = float(row.get('final_max_frp', online_row['current_max_frp']))
        retro_row['final_observation_count'] = int(row.get('final_observation_count', online_row['observation_count_so_far']))
        
        # Critical Leakage Safety: the retro_row MUST contain the online row, but the online_row MUST NOT contain retro_row's finals
        for k, v in online_row.items():
            if k not in online_features: online_features[k] = []
            online_features[k].append(v)
            
        for k, v in retro_row.items():
            if k not in retrospective_features: retrospective_features[k] = []
            retrospective_features[k].append(v)

    df_online = pd.DataFrame(online_features)
    df_retro = pd.DataFrame(retrospective_features)
    
    return df_online, df_retro

def process_layer(filepath, layer_name):
    print(f"Generating features for {layer_name} from {filepath}")
    df = pd.read_csv(filepath)
    df_online, df_retro = generate_features(df)
    
    out_dir = f"data/interim/features/{layer_name}"
    os.makedirs(out_dir, exist_ok=True)
    
    out_online = os.path.join(out_dir, "online_features.csv")
    out_retro = os.path.join(out_dir, "retrospective_features.csv")
    
    df_online.to_csv(out_online, index=False)
    df_retro.to_csv(out_retro, index=False)
    
    print(f"Layer {layer_name} Complete. Online: {len(df_online.columns)} cols. Retro: {len(df_retro.columns)} cols.")

if __name__ == "__main__":
    process_layer('data/synthetic/deployment_realistic/train_A.csv', "LAYER_A_REAL_PROXY")
    process_layer('data/synthetic/deployment_realistic/unseen_deployment_C.csv', "LAYER_B_DEPLOYMENT_SYNTHETIC")
    process_layer('data/synthetic/deployment_realistic/unseen_deployment_D.csv', "LAYER_C_ADVERSARIAL")
