# Canonical Feature Pipeline

## 1. Overview
The Canonical Feature Pipeline standardizes the transformation of raw thermal anomaly events into a robust, structured feature vector used by Agni-Netra's intelligence layers. This pipeline strictly enforces data leakage boundaries and handles missing evidence systematically.

**Schema Version:** `AGN-FEATURES-1.0`

## 2. Feature Schema

The pipeline produces an instance of `CanonicalEventFeatures` which groups features into logical domains:

### THERMAL
- `current_max_frp`: Max FRP observed to date.
- `current_mean_frp`: Mean FRP observed.
- `frp_std`: Standard deviation of FRP.
- `recent_frp_trend`: Trajectory of recent FRP values.
- `frp_change_rate`: Rate of change between observations.

### TEMPORAL
- `observation_count_so_far`: Cumulative number of observations.
- `event_age`: Time elapsed since the first detection (duration).
- `persistence`: Duration of contiguous activity.
- `observation_spacing`: Average time gap between sequential observations.
- `recent_activity`: Recency proxy.
- `time_since_last_detection`: Gap since the last observation.

### SPATIAL / MORPHOLOGY
- `spatial_extent`: Bounding box or spread approximation.
- `centroid_shift`: Displacement of the event center over time.
- `footprint_change`: Rate of growth in area.
- `spatial_density`: Number of observations per area unit.

### FACILITY / CONTEXT
- `distance_to_industrial_context`: Distance to nearest mapped infrastructure.
- `facility_context_type`: Categorical label for facility type.
- `nearby_industrial_flag`: Binary indicator (1 if near industry, 0 otherwise).
- `land_context`: Environmental mapping proxy.

### HISTORICAL
- `historical_event_frequency`: Historic density.
- `historical_mean_frp`: 90-day historic typical thermal power.
- `historical_typical_duration`: 90-day typical length.
- `historical_recurrence`: Probability of repeating event.
- `historical_frp_deviation`: Ratio of current FRP vs historic baseline.

### ANOMALY & DATA QUALITY
- `anomaly_score`: Deviation from physical baselines.
- `change_point_indicator`: Sudden spike triggers.
- `observation_quality`: Confidence metric from sensor array.

## 3. Leakage & Missingness Policy

### Data Leakage Safety
The pipeline operates in two modes: `online` (default) and `retrospective`.
- In `online` mode, fields strictly designated as `RETROSPECTIVE_ONLY` (such as `retro_final_duration`, `retro_final_max_frp`) are wiped to `NaN`. This guarantees that future timeline information never bleeds into real-time operational inference.

### Missing Data Representation
Missingness is treated as *information*. Explicit binary indicators are toggled when data streams are absent:
- `sentinel_available` (0 if no optical evidence exists)
- `missing_history_indicator`
- `missing_context_indicator`
- `missing_sensor_indicator`

When indicators are tripped, the respective continuous values are populated with `NaN` (or mapped safely in the inference wrapper) rather than artificially zero-filled.

## 4. Downstream Integration (Phase 16E-R2)
The frozen models established in Phase 16E-R2 consume this new canonical object via a bridge API (`predict_event_canonical`). The bridge:
1. Receives raw inputs.
2. Yields the `CanonicalEventFeatures` vector (wiping leakages automatically).
3. Maps the structured schema into the raw numpy/tensor geometries expected by the underlying frozen architecture, keeping the frozen models untouched while standardizing the upstream data flow.
