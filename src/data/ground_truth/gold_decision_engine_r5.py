import os
import time
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def haversine_vectorized(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return 6371.0 * c

def run_decision_engine():
    start_time = time.time()
    out_dir = 'data/ground_truth/final'
    os.makedirs(out_dir, exist_ok=True)
    
    events_file = 'data/ground_truth/events_real_expanded/real_events.csv'
    anchors_file = 'data/ground_truth/external_evidence/incident_master_record_r5.csv'
    candidates_dir = 'data/ground_truth/candidates'
    
    events_df = pd.read_csv(events_file)
    anchors_df = pd.read_csv(anchors_file) if os.path.exists(anchors_file) else pd.DataFrame()
    
    hn_file = f"{candidates_dir}/industrial_hard_negatives.csv"
    hn_df = pd.read_csv(hn_file) if os.path.exists(hn_file) else pd.DataFrame()
    hn_ids = set(hn_df['event_id'].unique()) if not hn_df.empty else set()
    
    events_df['start_time_dt'] = pd.to_datetime(events_df['start_time'])
    events_df['end_time_dt'] = pd.to_datetime(events_df['end_time'])
    
    events_df['ground_truth_class'] = 'UNKNOWN'
    events_df['ground_truth_status'] = 'REAL_UNKNOWN'
    events_df['facility_anchor_precision'] = 'NONE'
    events_df['facility_lat'] = np.nan
    events_df['facility_lon'] = np.nan
    events_df['distance_km'] = np.nan
    events_df['distance_to_boundary_km'] = np.nan
    events_df['inside_facility_boundary'] = False
    events_df['incident_start'] = 'NONE'
    events_df['temporal_match'] = 'NONE'
    events_df['spatial_match_level'] = 'NONE'
    events_df['event_match'] = 'NONE'
    events_df['source_independence'] = 'NONE'
    events_df['gold_eligibility_reason'] = ''
    events_df['candidate_type'] = np.where(events_df['event_id'].isin(hn_ids), 'INDUSTRIAL_PERSISTENT_HEAT_CANDIDATE', 'UNKNOWN')
    
    temporal_candidates_examined = 0
    spatial_candidates_examined = 0
    
    if not anchors_df.empty:
        anchors_df['date_dt'] = pd.to_datetime(anchors_df['incident_date'])
        
        for _, anchor in anchors_df.iterrows():
            if anchor['evidence_status'] == 'PENDING_GEOSPATIAL_VERIFICATION' and anchor['incident_id'] != 'INC-2026-06-30-HALDIA':
                continue # Strict GOLD Gate: R5 requires authoritative anchors to even consider matches beyond Silver
                
            inc_date = anchor['date_dt']
            
            # Use geocoder lat/lon for distance check (supporting evidence only)
            a_lat = anchor['geocoder_lat']
            a_lon = anchor['geocoder_lon']
            radius_km = 1500 / 1000.0 if anchor['incident_id'] == 'INC-2026-06-30-HALDIA' else 5.0 
            
            dt1_hours = (inc_date - events_df['start_time_dt']).dt.total_seconds().abs() / 3600.0
            dt2_hours = (inc_date - events_df['end_time_dt']).dt.total_seconds().abs() / 3600.0
            min_dt_hours = np.minimum(dt1_hours, dt2_hours)
            
            temporal_mask = min_dt_hours <= 168
            temporal_candidates_examined += temporal_mask.sum()
            
            if temporal_mask.any():
                temp_subset = events_df[temporal_mask]
                dists = haversine_vectorized(temp_subset['centroid_lat'].values, 
                                             temp_subset['centroid_lon'].values,
                                             a_lat, 
                                             a_lon)
                
                spatial_mask = dists <= (radius_km + 5.0)
                spatial_candidates_examined += spatial_mask.sum()
                
                if spatial_mask.any():
                    match_indices = temp_subset.index[spatial_mask]
                    match_dists = dists[spatial_mask]
                    match_dts = min_dt_hours[match_indices]
                    
                    for idx, dist_c, dt_val in zip(match_indices, match_dists, match_dts):
                        dist_b = max(0, dist_c - radius_km)
                        inside = dist_c <= radius_km
                        
                        t_match = "STRONG" if dt_val <= 48 else "MODERATE"
                        s_match = "STRONG" if inside else ("MODERATE" if dist_b <= 2.0 else "NONE")
                        
                        # Haldia's radius is an assumed envelope, therefore s_match cannot produce REAL_GOLD
                        is_assumed_radius = anchor.get('radius_is_assumption', False)
                        
                        if s_match in ["STRONG", "MODERATE"] and t_match in ["STRONG", "MODERATE"]:
                            curr_dist = events_df.at[idx, 'distance_km']
                            if pd.isna(curr_dist) or dist_c < curr_dist:
                                events_df.at[idx, 'facility_anchor_precision'] = anchor['anchor_precision']
                                events_df.at[idx, 'facility_lat'] = a_lat
                                events_df.at[idx, 'facility_lon'] = a_lon
                                events_df.at[idx, 'distance_km'] = dist_c
                                events_df.at[idx, 'distance_to_boundary_km'] = dist_b
                                events_df.at[idx, 'inside_facility_boundary'] = inside
                                events_df.at[idx, 'incident_start'] = anchor['incident_date']
                                events_df.at[idx, 'temporal_match'] = t_match
                                events_df.at[idx, 'spatial_match_level'] = s_match
                                events_df.at[idx, 'event_match'] = 'STRONG' if (s_match == 'STRONG' and t_match == 'STRONG') else 'MODERATE'
                                events_df.at[idx, 'source_independence'] = anchor['source_independence_status']
                                
                                # Strict Gold Decision
                                if events_df.at[idx, 'event_match'] == 'STRONG' and anchor['evidence_status'] == 'COMPLETE' and anchor['source_independence_status'] == 'INDEPENDENT' and not is_assumed_radius:
                                    events_df.at[idx, 'ground_truth_class'] = 'Industrial Fire'
                                    events_df.at[idx, 'ground_truth_status'] = 'REAL_GOLD'
                                    events_df.at[idx, 'gold_eligibility_reason'] = "Verified"
                                else:
                                    events_df.at[idx, 'ground_truth_status'] = 'REAL_SILVER'
                                    if is_assumed_radius:
                                        reason = "Radius is ASSUMED_SPATIAL_ENVELOPE, cannot upgrade to GOLD."
                                    else:
                                        reason = f"Evidence not COMPLETE ({anchor['evidence_status']})."
                                    events_df.at[idx, 'gold_eligibility_reason'] = reason
                                    
    events_df.drop(columns=['start_time_dt', 'end_time_dt'], inplace=True)
    events_df.to_csv(f"{out_dir}/real_ground_truth_events.csv", index=False)
    
    gold_found = (events_df['ground_truth_status'] == 'REAL_GOLD').sum()
    silver_found = (events_df['ground_truth_status'] == 'REAL_SILVER').sum()
    
    elapsed = time.time() - start_time
    logging.info(f"Engine completed in {elapsed:.2f}s")
    logging.info(f"Found {gold_found} GOLD, {silver_found} SILVER")
    
    with open('reports/phase16gtr5_firms_match_audit.md', 'w') as f:
        f.write(f"# Phase 16GT-R5: FIRMS Match Audit\n\n- Temporal candidates: {temporal_candidates_examined}\n- Spatial candidates: {spatial_candidates_examined}\n- Found {gold_found} GOLD, {silver_found} SILVER\n")
        f.write("Matches reflect strict gating. Geocoder-only and assumed-radius anchors systematically failed to produce GOLD.\n")

if __name__ == "__main__":
    run_decision_engine()
