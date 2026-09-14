import hashlib
import json
import os

# Feature Registry Definition
# Enforces Provenance, Availability, and Schema constraints.

FEATURE_REGISTRY = {
    "version": "1.0",
    "features": {
        # A. CURRENT THERMAL FEATURES
        "current_max_frp": {
            "group": "THERMAL", "availability": "ONLINE_AVAILABLE", "provenance": "REAL_FIRMS",
            "source_columns": ["frp"], "interpretation": "Maximum FRP observed in the event up to T_current",
            "missingness": "Required", "type": "float"
        },
        "current_mean_frp": {
            "group": "THERMAL", "availability": "ONLINE_AVAILABLE", "provenance": "REAL_FIRMS",
            "source_columns": ["frp"], "interpretation": "Mean FRP up to T_current",
            "missingness": "Required", "type": "float"
        },
        "current_bright_ti4": {
            "group": "THERMAL", "availability": "ONLINE_AVAILABLE", "provenance": "REAL_FIRMS",
            "source_columns": ["bright_ti4"], "interpretation": "Max Brightness temp band 4 up to T_current",
            "missingness": "Required", "type": "float"
        },
        
        # B. TEMPORAL BEHAVIOR
        "observation_count_so_far": {
            "group": "TEMPORAL", "availability": "ONLINE_AVAILABLE", "provenance": "REAL_FIRMS",
            "source_columns": ["acq_date", "acq_time"], "interpretation": "Cumulative observation count",
            "missingness": "Required", "type": "int"
        },
        "current_event_duration_hours": {
            "group": "TEMPORAL", "availability": "ONLINE_AVAILABLE", "provenance": "REAL_FIRMS",
            "source_columns": ["acq_date", "acq_time"], "interpretation": "Hours from first observation to T_current",
            "missingness": "Required", "type": "float"
        },
        "inter_observation_gap_median": {
            "group": "TEMPORAL", "availability": "ONLINE_AVAILABLE", "provenance": "REAL_FIRMS",
            "source_columns": ["acq_date", "acq_time"], "interpretation": "Median gap between observations in hours",
            "missingness": "NaN if obs < 2", "type": "float"
        },
        
        # C. SPATIAL / OBSERVATION PROXIES (Corrected per User Instructions)
        "centroid_shift_distance_km": {
            "group": "SPATIAL", "availability": "ONLINE_AVAILABLE", "provenance": "REAL_FIRMS",
            "source_columns": ["latitude", "longitude"], "interpretation": "Distance from T_0 centroid to T_current centroid",
            "missingness": "0.0 if obs < 2", "type": "float"
        },
        "spatial_observation_density": {
            "group": "SPATIAL", "availability": "ONLINE_AVAILABLE", "provenance": "REAL_FIRMS",
            "source_columns": ["latitude", "longitude"], "interpretation": "Observations per sq km bounding box proxy",
            "missingness": "NaN if bounding box is 0", "type": "float"
        },
        "observation_expansion_rate": {
            "group": "SPATIAL", "availability": "ONLINE_AVAILABLE", "provenance": "REAL_FIRMS",
            "source_columns": ["latitude", "longitude", "acq_date", "acq_time"], "interpretation": "Rate of bounding box proxy growth over time",
            "missingness": "NaN if obs < 3", "type": "float"
        },
        
        # D. HISTORICAL FINGERPRINT
        "frp_vs_historical_median": {
            "group": "HISTORICAL", "availability": "ONLINE_AVAILABLE", "provenance": "DERIVED_REAL",
            "source_columns": ["frp", "hist_median_frp"], "interpretation": "Ratio of current max FRP to historical 90-day median",
            "missingness": "NaN if no history", "type": "float"
        },
        "history_insufficient_flag": {
            "group": "HISTORICAL", "availability": "ONLINE_AVAILABLE", "provenance": "DERIVED_REAL",
            "source_columns": ["hist_observation_count"], "interpretation": "Explicit indicator of sparse 90-day history",
            "missingness": "Required", "type": "int"
        },
        
        # E. ANOMALY / CHANGE (MODEL DERIVED)
        "anomaly_state_score": {
            "group": "ANOMALY", "availability": "ONLINE_AVAILABLE", "provenance": "MODEL_DERIVED",
            "source_columns": ["b1_anomaly"], "interpretation": "B1 Deviation from expected behavior",
            "missingness": "Required", "type": "float"
        },
        
        # F. SATELLITE EVIDENCE (SENTINEL)
        "sentinel_available": {
            "group": "SENTINEL", "availability": "ONLINE_AVAILABLE", "provenance": "REAL_SENTINEL_METADATA",
            "source_columns": ["s2_image"], "interpretation": "Is valid optical imagery available?",
            "missingness": "Required", "type": "int"
        },
        "sentinel_ndvi_proxy": {
            "group": "SENTINEL", "availability": "ONLINE_AVAILABLE", "provenance": "REAL_SENTINEL_RASTER",
            "source_columns": ["s2_ndvi"], "interpretation": "NDVI surrounding the event centroid",
            "missingness": "NaN if imagery missing", "type": "float"
        },
        
        # G. GEOGRAPHIC / FACILITY CONTEXT
        "industrial_context_strength": {
            "group": "CONTEXT", "availability": "CONTEXT_ONLY", "provenance": "REAL_OSM_CONTEXT",
            "source_columns": ["osm_distance"], "interpretation": "Proximity proxy to industrial infrastructure",
            "missingness": "0.0 if missing", "type": "float"
        },
        
        # RETROSPECTIVE ONLY FEATURES
        "final_event_duration_hours": {
            "group": "TEMPORAL", "availability": "RETROSPECTIVE_ONLY", "provenance": "REAL_FIRMS",
            "source_columns": ["acq_date", "acq_time"], "interpretation": "Total hours for the entire completed event",
            "missingness": "Required", "type": "float"
        },
        "final_max_frp": {
            "group": "THERMAL", "availability": "RETROSPECTIVE_ONLY", "provenance": "REAL_FIRMS",
            "source_columns": ["frp"], "interpretation": "Maximum FRP across the entire event lifecycle",
            "missingness": "Required", "type": "float"
        }
    }
}

def generate_registry_hash():
    schema_str = json.dumps(FEATURE_REGISTRY, sort_keys=True)
    return hashlib.sha256(schema_str.encode('utf-8')).hexdigest()

def export_registry(out_dir="data/interim/features"):
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "feature_registry_v1.json")
    
    registry_data = FEATURE_REGISTRY.copy()
    registry_data['registry_hash'] = generate_registry_hash()
    
    with open(out_path, 'w') as f:
        json.dump(registry_data, f, indent=4)
    print(f"Feature Registry V1 exported to {out_path}")
    print(f"Registry Hash: {registry_data['registry_hash']}")

if __name__ == "__main__":
    export_registry()
