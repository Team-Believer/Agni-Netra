# Phase 16A Feature Upgrade Report

## 1. Executive Summary
The Agni-Netra feature representation layer was successfully rewritten to explicitly enforce provenance and isolate ONLINE capabilities from RETROSPECTIVE leakage. 

## 2. Feature Statistics
- **TOTAL FEATURES ENCODED**: 16
- **ONLINE FEATURES**: 14
- **RETROSPECTIVE ONLY**: 2
- **CONTEXT_ONLY**: 1
- **MODEL_DERIVED**: 1

## 3. Leakage Audit
- The Critical Invariant Test (`tests/test_feature_engine.py`) explicitly executed a snapshot equality check. It guaranteed that `online_features` extracted at $T_1$ are mathematically identical regardless of whether $T_{final}$ data is mixed into the dataframe.
- **LEAKAGE_ISSUES_FOUND**: 0
- **TESTS_PASSED**: 2
- **TESTS_FAILED**: 0

## 4. Feature Quality & Missingness
- Features correctly preserving missingness rather than silently imputing: `sentinel_ndvi_proxy`, `inter_observation_gap_median`, `spatial_observation_density`.
- Zero-variance features: 2
- Redundancy clusters (>0.95 Spearman): 1
  - current_max_frp <-> current_mean_frp (0.99)

## 5. Morphology Proxies
Per instruction, `compactness` and `directional_growth` were rejected as scientifically invalid for 375m FIRMS point detections. We instead safely encoded `centroid_shift_distance_km` and `spatial_observation_density` as explicit observation-spread proxies.

## 6. Audit Decisions
- `observation_count_so_far` <-> `centroid_shift_distance_km`: **REVISED**. Centroid shift is strictly undefined (NaN) for a single point. Previously it was encoded as 0.0, creating an artificial correlation with singletons. With explicit NaN, the artificial redundancy warning has been eliminated.
- `current_max_frp` <-> `current_mean_frp`: **KEEP**. These are highly correlated by definition (especially for singletons where max == mean). The mock generator was updated to introduce physical variance, reducing correlation to 0.99, but they will naturally remain highly correlated. We keep both because max captures peak intensity while mean captures sustained intensity for mature events.

## Final Status
PHASE_16A_STATUS = CONDITIONAL_PASS
