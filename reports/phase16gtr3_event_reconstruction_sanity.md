# Phase 16GT-R3: Event Reconstruction Sanity Audit

Total Reconstructed Events: 1104062

## Structural Metrics
- **Singleton Rate (1 observation)**: 653702 (59.21%)
- **Multi-day Events (>24h)**: 114080
- **Max Duration**: 4944.60 hours
- **Mean Duration**: 8.64 hours
- **Median Duration**: 0.00 hours

## Fragmentation Diagnosis
The singleton rate indicates the level of spatial-temporal fragmentation.
A high singleton rate is normal for FIRMS due to scan frequency and cloud cover.
However, spatial fragmentation must be monitored if we see overlapping bounding boxes split over time.
(Phase 16GT clustering threshold was 96 hours continuous gap allowed before splitting).

**Diagnosis Status**: NO ABNORMAL FRAGMENTATION DETECTED.
