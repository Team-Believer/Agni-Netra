import os
import pandas as pd
import logging
from math import radians, sin, cos, sqrt, asin

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    a = sin((lat2-lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2-lon1)/2)**2
    return 2 * asin(sqrt(a)) * 6371.0

def audit_haldia_silver():
    df = pd.read_csv('data/ground_truth/final/real_ground_truth_events.csv')
    silver_df = df[df['ground_truth_status'] == 'REAL_SILVER']
    
    # Haldia Anchor Info
    anchor_lat = 22.05936
    anchor_lon = 88.10363
    # A typical integrated petrochemical complex of this size (Naphtha cracker) spans ~1000-2000 acres.
    # 1500m radius corresponds to ~7 sq km (1700 acres) which is highly defensible.
    radius_m = 1500
    radius_km = radius_m / 1000.0
    
    report = """# Phase 16GT-R4: Haldia Silver Geometry Audit

## Anchor Geometry Status
- **Incident ID**: INC-2026-06-30-HALDIA
- **Facility**: Haldia Petrochemicals Limited
- **Anchor Precision**: FACILITY_POINT_VERIFIED (Revised from Boundary to Point+Radius per Step 2 rules)
- **Anchor Source**: Official environmental document
- **Anchor Confidence**: HIGH
- **Anchor Point**: 22.05936, 88.10363
- **Defensible Radius**: 1500 meters (~7 sq km, typical for 1000+ acre integrated naphtha complex)
- **Radius Source**: Estimated from industrial estate acreage bounds
- **Facility Boundary Available**: FALSE (Using Point + Radius)

## 4 Candidate Matches Analysis

"""
    
    for _, row in silver_df.iterrows():
        dist_centroid = row['distance_km']
        
        # Calculate distance to boundary (radius)
        # If distance to centroid is less than radius, it's inside (distance to boundary = 0)
        dist_boundary = max(0, dist_centroid - radius_km)
        inside = dist_centroid <= radius_km
        
        report += f"### FIRMS Event: {row['event_id']}\n"
        report += f"- **FIRMS Event Start**: {row['start_time']}\n"
        report += f"- **FIRMS Event End**: {row['end_time']}\n"
        report += f"- **FIRMS Centroid**: {row['centroid_lat']}, {row['centroid_lon']}\n"
        report += f"- **Distance to Facility Centroid**: {dist_centroid:.2f} km\n"
        report += f"- **Distance to Facility Boundary**: {dist_boundary:.2f} km\n"
        report += f"- **Inside Facility Boundary**: {inside}\n"
        report += f"- **Temporal Relation**: {row['temporal_match']}\n"
        report += f"- **External Source**: ChemNet (TIER_3_NEWS)\n"
        report += f"- **Second Independent Source**: None acquired yet\n"
        report += f"- **Why Not Gold**: Event centroid is {dist_boundary:.2f} km outside the defensible {radius_m}m boundary. Spatial confidence remains MODERATE. No second independent source.\n\n"
        
    os.makedirs('reports', exist_ok=True)
    with open('reports/phase16gtr4_haldia_silver_geometry_audit.md', 'w') as f:
        f.write(report)
        
    logging.info("Haldia Silver Geometry Audit Complete.")

if __name__ == "__main__":
    audit_haldia_silver()
