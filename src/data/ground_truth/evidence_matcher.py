import os
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

def match_evidence():
    events_file = 'data/ground_truth/events_real_expanded/real_events.csv'
    evidence_file = 'data/ground_truth/external_evidence/validated_external_evidence.csv'
    out_dir = 'data/ground_truth/external_evidence'
    
    if not os.path.exists(events_file) or not os.path.exists(evidence_file):
        logging.error("Missing events or evidence file.")
        return
        
    events_df = pd.read_csv(events_file)
    evidence_df = pd.read_csv(evidence_file)
    
    events_df['first_detected'] = pd.to_datetime(events_df['first_detected'])
    events_df['last_detected'] = pd.to_datetime(events_df['last_detected'])
    evidence_df['date'] = pd.to_datetime(evidence_df['date'])
    
    matches = []
    
    for _, ev in events_df.iterrows():
        eid = ev['event_id']
        elat = ev['centroid_lat']
        elon = ev['centroid_lon']
        efirst = ev['first_detected']
        elast = ev['last_detected']
        
        for _, ext in evidence_df.iterrows():
            ext_lat = ext['latitude']
            ext_lon = ext['longitude']
            ext_date = ext['date']
            
            # Spatial distance
            dist_km = haversine_km(elat, elon, ext_lat, ext_lon)
            
            # Temporal distance (closest to either first or last detection)
            dt1 = abs((ext_date - efirst).total_seconds() / 86400.0)
            dt2 = abs((ext_date - elast).total_seconds() / 86400.0)
            min_dt_days = min(dt1, dt2)
            
            if dist_km <= 25.0 and min_dt_days <= 14.0:
                matches.append({
                    'event_id': eid,
                    'incident_id': ext['incident_id'],
                    'distance_km': dist_km,
                    'time_delta_days': min_dt_days,
                    'tier': ext['tier'],
                    'source_url': ext['source_url']
                })
                
    matches_df = pd.DataFrame(matches)
    if matches_df.empty:
        matches_df = pd.DataFrame(columns=['event_id', 'incident_id', 'distance_km', 'time_delta_days', 'tier', 'source_url'])
        
    matches_df.to_csv(f"{out_dir}/matched_evidence.csv", index=False)
    logging.info(f"Generated {len(matches_df)} evidence matches.")

if __name__ == "__main__":
    match_evidence()
