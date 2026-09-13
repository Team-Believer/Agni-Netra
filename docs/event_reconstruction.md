# Agni-Netra Phase 4: Event Reconstruction Strategy

## Objective
Convert individual, snapshot FIRMS observations into robust, persistent physical-event candidates without relying on weak Phase 3 labels.

## Configurable Parameters
All parameters are stored in `configs/event_reconstruction.yaml`:
- **spatial_radius_km (1.0 km)**: Maximum distance between observations to be considered the same physical source.
- **minimum_samples (2)**: Threshold for a spatial cluster before it's considered non-noise (noise is treated as singletons).
- **event_continuation_window (72 hours)**: Maximum time gap allowed. If the gap exceeds this, the event is fragmented into a new incident (e.g., a new fire starting at an old burn scar).

## Method Tested: Spatial DBSCAN + Temporal Fragmentation
We evaluated a hybrid strategy:
1. **Spatial Clustering (Strategy A)**: We used the Haversine metric to account for spherical geometry and clustered points within 1.0 km of each other.
2. **Temporal Association (Strategy B)**: For each spatial cluster, we sorted observations chronologically. We then stepped through time; if the gap between consecutive observations exceeded 72 hours, we logically fragmented the cluster into a new `event_id`.

### Why this method?
- **Industrial Event Fragmentation**: Stationary industrial heat (e.g. flares) will naturally form dense spatial clusters. By allowing long continuation windows (72h), we avoid incorrectly fragmenting a flare into daily "new" fires just because it was obscured by clouds for a day.
- **Satellite Independence**: NOAA-20 and S-NPP detections fall into the same spatial cluster. The temporal sort easily intertwines them chronologically, perfectly aggregating complementary satellite coverage.
- **Intermittency**: 197 events were flagged as "Intermittently Observable" (duration > 24h, but very sparse hits), retaining their identity despite observation gaps.

## Event State Definitions
- **Detected**: Singleton observation.
- **Emerging**: Multi-observation, duration > 12 hours.
- **Persistent**: Duration > 48 hours.
- **Intermittently Observable**: Duration > 24h, but sparse (< 1 hit per 12 hours).

## Quality Checks
- We successfully handle duplicate observations (they simply add to the observation count with zero temporal gap).
- Coordinates are validated to be strictly within global bounds.
- Events cannot have a temporal gap exceeding 72h; if they do, they are split (preventing infinite creeping events).
