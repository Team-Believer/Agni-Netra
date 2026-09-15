import os
import json
import logging
import pandas as pd
from shapely.geometry import box, Point

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_osm_context(target_type):
    context_path = 'data/raw/osm/context.geojson'
    if not os.path.exists(context_path):
        return []
    
    with open(context_path, 'r') as f:
        data = json.load(f)
        
    boxes = []
    for feature in data.get('features', []):
        props = feature.get('properties', {})
        if props.get('type') == target_type:
            bbox = feature.get('bbox')
            if bbox and len(bbox) == 4:
                min_lon, min_lat, max_lon, max_lat = bbox
                boxes.append(box(min_lon, min_lat, max_lon, max_lat))
                
    return boxes

def is_in_boxes(lat, lon, boxes):
    pt = Point(lon, lat)
    for b in boxes:
        if pt.within(b):
            return True
    return False

def discover_ag_burns():
    events_file = 'data/ground_truth/events_real_expanded/real_events.csv'
    out_dir = 'data/ground_truth/candidates'
    
    if not os.path.exists(events_file):
        logging.error(f"Events file {events_file} not found.")
        return
        
    df = pd.read_csv(events_file)
    ag_boxes = load_osm_context('farmland')
    
    df['is_ag'] = df.apply(lambda row: is_in_boxes(row['centroid_lat'], row['centroid_lon'], ag_boxes), axis=1)
    
    # Exclude persistent (which could be misclassified flares) and ensure very short duration
    ag_burns = df[(df['is_ag'] == True) & (df['duration_hours'] <= 48)].copy()
    
    os.makedirs(out_dir, exist_ok=True)
    ag_burns.to_csv(f"{out_dir}/agricultural_candidates.csv", index=False)
    
    logging.info(f"Discovered {len(ag_burns)} Agricultural Burn candidates based on farmland context.")

if __name__ == "__main__":
    discover_ag_burns()
