# Phase 14 Final Report: Risk, Priority & Decision Intelligence

> [!NOTE]
> Agni-Netra computes interpretable development risk and priority indices from multiple evidence dimensions. 
> REAL-WORLD RISK CALIBRATION: NOT ESTABLISHED.
> REAL-WORLD OPERATIONAL IMPACT: NOT VALIDATED.

## 1. Engine Architecture
The decision intelligence layer successfully disentangled the previously opaque classification model into explicit operational concepts.

- **Severity Engine**: Computes intensity (FRP + Duration) independent of location.
- **Impact Engine**: Computes consequence/exposure independent of severity.
- **Hazard Engine**: Contextualizes Severity with the Classification State (e.g. Industrial Fires inherit full hazard potential, whereas Routine Flares are heavily discounted).
- **Risk Engine**: `Base Risk = Hazard * Impact`. It strictly measures the theoretical physical danger of the event.
- **Risk Confidence**: Explicitly tracks the availability and consistency of underlying data (Evidence Completeness, Data Quality, Classification Confidence).
- **Priority Engine**: Combines Base Risk, Risk Confidence, and Temporal Urgency. This routes the event to the correct operator queue (P0 to P4).

## 2. Explainability (`WHY` / `WHY NOT`)
The Explanation Engine maps quantitative evidence scores deterministically to human-readable strings, guaranteeing auditability.

**Example 1 (High Risk, High Priority)**:
- `CLASSIFICATION`: Industrial Fire (Confidence: 0.88)
- `RISK`: 0.85
- `PRIORITY`: P0 - IMMEDIATE REVIEW
- `WHY`: FRP is substantially above the historical baseline. | High exposure context detected. | Behavioral signature strongly aligns with Industrial Fire.
- `WHAT CHANGED`: Rapid increase in FRP detected.

**Example 2 (Low Risk, High Uncertainty)**:
- `CLASSIFICATION`: Unknown
- `RISK`: 0.12
- `PRIORITY`: P3 - REQUEST MORE DATA
- `WHY NOT`: Classification confidence is below actionable threshold. | Sentinel-2 imagery is unavailable or cloudy.
- `WHAT IS UNKNOWN`: Missing Sentinel-2 imagery. | Classification unresolved (Unknown).
- `ACTION`: VERIFY_SOURCE_AND_CLASS

## 3. Synthetic Validation
The decision layer was validated on Generator C using independent latent exposure variables, completely breaking the circularity of using proxy context for both classification and exposure. 

Monotonicity and Routing Tests passed perfectly:
- Risk monotonically increases with Hazard/Impact.
- High Uncertainty explicitly blocks High Priority physical alerts (P0), but correctly triggers High Priority verification (P1).
- Missing data explicitly triggers the `WHAT_IS_UNKNOWN` explanation rather than creating false certainty.

## 4. Recommended Action & Next Steps
This completes Phase 14. The resulting `decision_table.csv` perfectly isolates Risk from Priority, and perfectly isolates Uncertainty from Hazard. The operational ruleset ensures that Agni-Netra will not confidently alert on missing data, but instead requests verification.

**Next Phase**: The architecture is fully prepared to be integrated into the final operational dashboard and event-ranking UI.
