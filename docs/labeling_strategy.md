# Agni-Netra Phase 3 Labeling Strategy

## Overview
This document details the provisional labeling strategy for the Agni-Netra AI Intelligence Layer, specifically mapping unverified FIRMS observations to the six-class MVP taxonomy using contextual evidence.

## The Six-Class Taxonomy and Evidence Rules

### 1. Routine Flare / Persistent Industrial Heat
- **Evidence Rule**: Must intersect an `industrial` facility polygon AND exhibit high 7-day spatial persistence (e.g., >10 observations in a 0.01-degree radius).
- **Quality**: `HIGH_CONFIDENCE_WEAK`.
- **Limitation**: 7 days is insufficient for a robust long-term fingerprint. Real routine flares operate for years, so these are currently just "candidates".

### 2. Industrial Fire
- **Evidence Rule**: Intersects an `industrial` facility polygon BUT lacks persistence (isolated event).
- **Quality**: `WEAK`.
- **Limitation**: Being inside a facility does not prove it is an uncontrolled fire; it could be a transient controlled burn, an anomaly, or an unusually bright routine flare. This is why facility context is not equivalent to an Industrial Fire label.

### 3. Wildfire
- **Evidence Rule**: Intersects `forest` context.
- **Quality**: `WEAK`.
- **Limitation**: Without an authoritative fire perimeter or verified incident report, this is a provisional candidate based solely on land cover.

### 4. Agricultural Burn
- **Evidence Rule**: Intersects `farmland` context.
- **Quality**: `WEAK`.
- **Limitation**: Land cover alone does not prove the nature of the fire; other anthropogenic fires can occur in farmlands.

### 5. Other Anthropogenic
- **Evidence Rule**: Specific context for non-industrial, non-agricultural human activity (e.g., landfills).
- **Currently**: Unassigned in our heuristic dataset due to lack of specific contextual polygons.

### 6. Unknown / Needs Verification
- **Evidence Rule**: Lack of context, or insufficient persistence, or conflicting context.
- **Quality**: `UNKNOWN`.
- **Limitation**: This acts as a necessary abstention class to prevent forcing unsupported labels onto ambiguous points.

## Conflict Handling
If a point intersects multiple incompatible contexts (e.g., `industrial` and `forest`), the `ambiguity_status` is set to `CONFLICTING`, and the label defaults to `Unknown / Needs Verification`.

## Known Biases and Limitations
- **Geographic Bias**: Using Overpass API dynamically limits context retrieval. We focused on the top 10 most dense hotspots, meaning isolated fires are overwhelmingly classified as UNKNOWN.
- **Temporal Bias**: The 7-day observation window severely limits our ability to confidently assert a "Routine Flare", which typically requires months of historical baseline.
- **Class Imbalance**: The vast majority (88%) of observations are classified as UNKNOWN because they lack overlapping facility context in our subset. This accurately reflects real-world uncertainty but presents a heavily imbalanced dataset for ML training.
