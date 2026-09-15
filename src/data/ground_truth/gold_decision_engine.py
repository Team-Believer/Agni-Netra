import os
import time
import pandas as pd
import numpy as np
import logging
from math import radians, sin, cos, sqrt, asin

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def haversine_vectorized(lat1, lon1, lat2, lon2):
    # lat1, lon1 can be arrays/series
    # lat2, lon2 are scalar floats
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return 6371.0 * c

def run_decision_engine(sample_size=None):
    start_time = time.time()
    
    out_dir = 'data/ground_truth/final'
    os.makedirs(out_dir, exist_ok=True)
    
    events_file = 'data/ground_truth/events_real_expanded/real_events.csv'
    anchors_file = 'data/ground_truth/external_evidence/geospatial_facility_anchors.csv'
    candidates_dir = 'data/ground_truth/candidates'
    
    events_df = pd.read_csv(events_file)
    if sample_size:
        events_df = events_df.head(sample_size).copy()
        
    anchors_df = pd.read_csv(anchors_file) if os.path.exists(anchors_file) else pd.DataFrame()
    
    hn_file = f"{candidates_dir}/industrial_hard_negatives.csv"
    hn_df = pd.read_csv(hn_file) if os.path.exists(hn_file) else pd.DataFrame()
    hn_ids = set(hn_df['event_id'].unique()) if not hn_df.empty else set()
    
    total_events = len(events_df)
    total_incidents = len(anchors_df)
    
    logging.info(f"Loaded {total_events} events and {total_incidents} incidents.")
    
    # 1. Parse all event datetimes ONCE
    parse_start = time.time()
    # Fast parsing with format if known, but just pd.to_datetime is vectorized enough over a column
    # Let's specify infer_datetime_format=True or format='%Y-%m-%d %H:%M:%S'
    events_df['start_time_dt'] = pd.to_datetime(events_df['start_time'])
    events_df['end_time_dt'] = pd.to_datetime(events_df['end_time'])
    logging.info(f"Datetime parsing completed in {time.time() - parse_start:.2f}s")
    
    # Defaults
    events_df['ground_truth_class'] = 'UNKNOWN'
    events_df['ground_truth_status'] = 'REAL_UNKNOWN'
    events_df['facility_anchor_precision'] = 'NONE'
    events_df['facility_lat'] = np.nan
    events_df['facility_lon'] = np.nan
    events_df['facility_source'] = 'NONE'
    events_df['facility_match'] = 'NONE'
    events_df['spatial_match_level'] = 'NONE'
    events_df['distance_km'] = np.nan
    events_df['incident_start'] = 'NONE'
    events_df['temporal_match'] = 'NONE'
    events_df['event_match'] = 'NONE'
    events_df['source_independence'] = 'NONE'
    events_df['gold_eligibility_reason'] = ''
    events_df['candidate_type'] = np.where(events_df['event_id'].isin(hn_ids), 'INDUSTRIAL_PERSISTENT_HEAT_CANDIDATE', 'UNKNOWN')
    
    events_df.loc[events_df['candidate_type'] == 'INDUSTRIAL_PERSISTENT_HEAT_CANDIDATE', 'gold_eligibility_reason'] = 'Persistent industrial thermal behavior alone does not independently verify Routine Flare.'
    
    temporal_candidates_examined = 0
    spatial_candidates_examined = 0
    
    # For each incident, find matching events efficiently
    if not anchors_df.empty:
        anchors_df['date_dt'] = pd.to_datetime(anchors_df['date'])
        
        for _, anchor in anchors_df.iterrows():
            inc_date = anchor['date_dt']
            
            # Temporal Window Filter: +/- 7 days (168 hours) max for MODERATE
            dt1_hours = (inc_date - events_df['start_time_dt']).dt.total_seconds().abs() / 3600.0
            dt2_hours = (inc_date - events_df['end_time_dt']).dt.total_seconds().abs() / 3600.0
            min_dt_hours = np.minimum(dt1_hours, dt2_hours)
            
            temporal_mask = min_dt_hours <= 168
            temporal_candidates_examined += temporal_mask.sum()
            
            # Only calculate distances for events within the temporal window
            if temporal_mask.any():
                temp_subset = events_df[temporal_mask]
                dists = haversine_vectorized(temp_subset['centroid_lat'].values, 
                                             temp_subset['centroid_lon'].values,
                                             anchor['anchor_lat'], 
                                             anchor['anchor_lon'])
                
                # Spatial mask
                spatial_mask = dists <= 5.0
                spatial_candidates_examined += spatial_mask.sum()
                
                if spatial_mask.any():
                    # We have candidates that match spatially and temporally
                    match_indices = temp_subset.index[spatial_mask]
                    match_dists = dists[spatial_mask]
                    match_dts = min_dt_hours[match_indices]
                    
                    for idx, dist, dt_val in zip(match_indices, match_dists, match_dts):
                        # Strict logic checks
                        t_match = "STRONG" if dt_val <= 48 else "MODERATE"
                        s_match = "STRONG" if dist <= 2.0 else "MODERATE"
                        
                        if anchor['anchor_precision'] in ['CITY_LEVEL', 'DISTRICT_LEVEL', 'FACILITY_APPROXIMATE', 'VILLAGE_LEVEL']:
                            s_match = "NONE"
                            
                        # Better than existing match? (Current logic didn't properly handle multi-match gracefully across incidents, but we just update if better)
                        # We'll just assign it if it matches
                        if s_match in ["STRONG", "MODERATE"] and t_match in ["STRONG", "MODERATE"]:
                            # Is this distance better than existing? (handle NaN)
                            curr_dist = events_df.at[idx, 'distance_km']
                            if pd.isna(curr_dist) or dist < curr_dist:
                                events_df.at[idx, 'facility_anchor_precision'] = anchor['anchor_precision']
                                events_df.at[idx, 'facility_lat'] = anchor['anchor_lat']
                                events_df.at[idx, 'facility_lon'] = anchor['anchor_lon']
                                events_df.at[idx, 'facility_source'] = anchor['anchor_source']
                                events_df.at[idx, 'facility_match'] = 'STRONG' if anchor['facility_identity_confidence'] == 'HIGH' else 'MODERATE'
                                events_df.at[idx, 'spatial_match_level'] = s_match
                                events_df.at[idx, 'distance_km'] = dist
                                events_df.at[idx, 'incident_start'] = anchor['date']
                                events_df.at[idx, 'temporal_match'] = t_match
                                events_df.at[idx, 'event_match'] = 'STRONG' if (s_match == 'STRONG' and t_match == 'STRONG') else 'MODERATE'
                                events_df.at[idx, 'source_independence'] = anchor['anchor_source_type']
                                
                                # Gold decision
                                if events_df.at[idx, 'facility_match'] == 'STRONG' and events_df.at[idx, 'event_match'] == 'STRONG':
                                    events_df.at[idx, 'ground_truth_class'] = 'Industrial Fire'
                                    events_df.at[idx, 'ground_truth_status'] = 'REAL_GOLD'
                                    events_df.at[idx, 'gold_eligibility_reason'] = f"Independently verified via {anchor['provider']} with {anchor['anchor_precision']} anchor."
                                else:
                                    events_df.at[idx, 'ground_truth_status'] = 'REAL_SILVER'
                                    events_df.at[idx, 'gold_eligibility_reason'] = f"Insufficient match strength (Spatial: {s_match}, Temporal: {t_match})."
                                    
    # Clean up temp columns
    events_df.drop(columns=['start_time_dt', 'end_time_dt'], inplace=True)
    
    if not sample_size:
        events_df.to_csv(f"{out_dir}/real_ground_truth_events.csv", index=False)
        
    gold_found = (events_df['ground_truth_status'] == 'REAL_GOLD').sum()
    silver_found = (events_df['ground_truth_status'] == 'REAL_SILVER').sum()
    
    elapsed = time.time() - start_time
    logging.info(f"Engine completed in {elapsed:.2f}s")
    logging.info(f"Temporal candidates: {temporal_candidates_examined}, Spatial: {spatial_candidates_examined}")
    logging.info(f"Found {gold_found} GOLD, {silver_found} SILVER")
    
    return events_df, elapsed, temporal_candidates_examined, spatial_candidates_examined, gold_found, silver_found

if __name__ == "__main__":
    run_decision_engine()
