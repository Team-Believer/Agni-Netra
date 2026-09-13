# Agni-Netra Phase 5A: Event Features Documentation

## Overview
This dataset condenses the 9,714 FIRMS observations into 3,302 physical-event vectors ready for ML modeling.

## 1. Feature Categories
* **THERMAL**: `mean_frp`, `max_frp`, `min_frp`, `frp_std`, `frp_cv`, `frp_first`, `frp_last`, `frp_change`, `brightness_mean`, `brightness_max`.
* **TEMPORAL**: `duration_hours`, `observation_count`, `obs_per_day`, `median_gap`, `max_gap`, `day_night_ratio`.
* **SPATIAL**: `spatial_spread_km` (approximate max bounding box diagonal).
* **SENSOR**: `num_satellites`.
* **BEHAVIOR**: `expanding_indicator`, `stable_indicator`, `sudden_frp_increase`.
* **QUALITY**: `min_confidence`, `mean_confidence`.
* **HISTORICAL**: `history_window_days`, `history_sufficiency`.

## 2. Missing Data Treatment
* If `frp` or `brightness` are missing, features fall back to 0.0 or `NaN`. However, FIRMS data is 100% complete for these fields in this dataset.
* Categorical mappings for confidence use nominal defaults: `low=1, nominal=2, high=3`.

## 3. Label Handling
Phase 3 Provisional Labels are attached to `event_id`s using the following aggregation logic:
* If all observations in an event share the same class, the event inherits that class with quality `WEAK_AGGREGATED`.
* If observations conflict (e.g. one obs says "Wildfire", another says "Industrial"), the event is assigned `Unknown / Needs Verification` with quality `AMBIGUOUS`.
* If no context exists, it remains `Unknown`.

## 4. Leakage Considerations and Temporal Assumptions
### EVENT-LEVEL OFFLINE CLASSIFICATION
**CRITICAL WARNING:** This feature matrix uses the *full reconstructed event history*. 
For example, `duration_hours` and `max_frp` rely on observing the fire until it completely finishes. 
* This dataset is appropriate for offline post-incident classification (e.g. classifying historical events for an evidence ledger).
* **It is NOT appropriate for real-time first-detection alerts**, because a real-time system does not know the final `duration_hours` or `max_frp` at the exact moment a fire starts.
* **Leakage Risk**: Any feature that requires `t > 0` (like `duration_hours`, `frp_last`) represents a high leakage risk if we falsely claim the model operates at `t = 0`.
