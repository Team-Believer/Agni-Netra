import os
import pandas as pd
import logging
import json
from shapely.geometry import shape, Point

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_discovery():
    events_file = 'data/ground_truth/events_real_expanded/real_events.csv'
    osm_file = 'data/raw/osm/context.geojson'
    out_dir = 'data/ground_truth/candidates'
    os.makedirs(out_dir, exist_ok=True)
    
    if not os.path.exists(events_file):
        logging.error("Events file not found.")
        return
        
    df = pd.read_csv(events_file)
    
    industrial_polys = []
    if os.path.exists(osm_file):
        with open(osm_file, 'r') as f:
            osm = json.load(f)
            for feat in osm.get('features', []):
                if feat.get('properties', {}).get('type') == 'industrial' and 'geometry' in feat:
                    industrial_polys.append(shape(feat['geometry']))
                    
    candidates = []
    hard_negatives = []
    
    for _, row in df.iterrows():
        pt = Point(row['centroid_lon'], row['centroid_lat'])
        is_industrial = any(poly.contains(pt) for poly in industrial_polys)
        
        # If no OSM file or we want to broadly capture high FRP as candidate too
        if is_industrial or (row.get('mean_frp', 0) > 20.0):
            event_dict = row.to_dict()
            
            # Step 5: All these are Industrial Candidates
            candidates.append(event_dict)
            
            # Step 6: Hard negatives based on persistence > 72h
            if row['duration_hours'] > 72:
                event_dict['candidate_type'] = 'INDUSTRIAL_PERSISTENT_HEAT_CANDIDATE'
                event_dict['rationale'] = 'Duration > 72h + Industrial Context'
                hard_negatives.append(event_dict)
                
    cand_df = pd.DataFrame(candidates)
    hn_df = pd.DataFrame(hard_negatives)
    
    if not cand_df.empty:
        cand_df.to_csv(f"{out_dir}/industrial_fire_candidates.csv", index=False)
    else:
        pd.DataFrame(columns=df.columns).to_csv(f"{out_dir}/industrial_fire_candidates.csv", index=False)
        
    if not hn_df.empty:
        hn_df.to_csv(f"{out_dir}/industrial_hard_negatives.csv", index=False)
    else:
        pd.DataFrame(columns=list(df.columns) + ['candidate_type', 'rationale']).to_csv(f"{out_dir}/industrial_hard_negatives.csv", index=False)
        
    logging.info(f"Discovered {len(cand_df)} Industrial Fire Candidates and {len(hn_df)} Hard Negatives.")

if __name__ == "__main__":
    run_discovery()
