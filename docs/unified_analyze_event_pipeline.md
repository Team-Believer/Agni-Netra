# Agni-Netra Unified Production Orchestrator: analyze_event() (Phase 18)

## 1. Executive Summary

`analyze_event()` is Agni-Netra's single production orchestration entry point. It connects the independently developed intelligence modules into one deterministic, end-to-end event analysis pipeline.

> **FOUNDATIONAL PRINCIPLE**:
> `analyze_event()` **ORCHESTRATES INFERENCE. IT DOES NOT REIMPLEMENT INFERENCE.**

The orchestrator preserves all upstream data contracts, controls execution order, gracefully handles missing evidence or optional sensor unavailability, and produces a single, versioned, JSON-serializable `EventIntelligenceResult`.

---

## 2. Pipeline Execution Flow

```
+-----------------------------------------------------------------------------------+
|                            INPUT EVENT DATA                                       |
|  (Raw observation dict / event contract / lat-lon / temporal time-series)         |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 1. INPUT VALIDATION                                                               |
|    Checks event identity, thermal FRP detections, & observation structure.         |
|    Failure -> returns structured FAILED / INSUFFICIENT_OBSERVATION result.        |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 2. CANONICAL EVENT FEATURES (Phase 17A)                                           |
|    Schema: AGN-FEATURES-1.1 (40 canonical features, online-safe & retro split).   |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 3. LOW-T PERSISTENT HEAT INTELLIGENCE (Phase 17B)                                 |
|    Evaluates moderate-intensity persistence, temporal stability, & recurrence.    |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 4. HISTORICAL ABNORMALITY & CHANGE ENGINE (Phase 17C)                             |
|    Computes deviations from historical baseline & multi-scale change indicators.  |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 5. MODEL / SOURCE INFERENCE                                                       |
|    Evaluates candidate probability vector across 9 source classes.                |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 6. EVIDENCE AGGREGATION & EVENT EVIDENCE LEDGER (Phase 17D)                       |
|    Constructs multi-family ledger & hypothesis support matrix.                    |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 7. CONFIDENCE CALIBRATION & UNKNOWN DECISION ENGINE (Phase 17E)                   |
|    Calibrates confidence & evaluates abstention hierarchy:                        |
|    INSUFFICIENT_OBSERVATION -> UNKNOWN -> NEEDS_VERIFICATION -> KNOWN.            |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 8. RISK & OPERATIONAL PRIORITY ENGINE (Phase 17F)                                 |
|    Calculates Base Risk = sqrt(Hazard * Impact), Urgency, & Priority (P0 - P4).   |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 9. WHY / WHY NOT / WHAT CHANGED EXPLANATION ENGINE (Phase 17G)                    |
|    Generates evidence-grounded operator summaries & provenance records.           |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        EVENT INTELLIGENCE RESULT                                  |
|  - Schema: AGN-EVENT-INTELLIGENCE-1.0                                             |
|  - Complete JSON-serializable structured output contract.                          |
+-----------------------------------------------------------------------------------+
```

---

## 3. Section Assessment Contracts (`EventIntelligenceResult`)

The output contract separates intelligence concepts rather than flattening scores into one dictionary:

1. **`event_id`**: Persistent unique string identifier.
2. **`event_metadata`**: Coordinates (`lat`, `lon`), observation count, duration in hours, mode (`online` / `retrospective`).
3. **`observation_summary`**: Data quality score, temporal sufficiency, historical sufficiency, sensor availability indicators.
4. **`source_assessment`**: Predicted source class, decision state, classifier confidence, model predictions across candidate classes.
5. **`behavior_assessment`**: Low-T state, behavior signal (`STABLE_PERSISTENT`, `RECURRING_PERSISTENT`, `TRANSIENT_OR_DEVELOPING`), thermal/spatial stability scores.
6. **`abnormality_assessment`**: Abnormality score, level (`NORMAL`, `UNUSUAL`, `HIGHLY_ABNORMAL`, `UNKNOWN`), change detected flag, change summary statements, history tier.
7. **`evidence_assessment`**: Complete event evidence ledger, evidence items, hypothesis support matrix, evidence completeness, convergence score.
8. **`confidence_assessment`**: Multi-dimensional confidence object, calibration status/method, abstention reason codes, limiting factors.
9. **`risk_assessment`**: Hazard score/level, impact score/level, base risk score, risk level, risk confidence.
10. **`priority_assessment`**: Operational priority score, priority level ($P0 \dots P4$), urgency level, operational action recommendation, priority drivers.
11. **`explanation`**: Summary text, `why`, `why_not`, `what_changed`, `uncertainty`, `next_action`, `provenance`.
12. **`verification`**: `verification_state` (`NOT_REQUIRED`, `REVIEW_RECOMMENDED`, `VERIFY_REQUIRED`, `INSUFFICIENT_DATA`, `HUMAN_VERIFIED`, `HUMAN_DISPUTED`).
13. **`pipeline_status`**: Execution status (`COMPLETE`, `PARTIAL`, `INSUFFICIENT_OBSERVATION`, `FAILED`), stage statuses dictionary, stage execution durations in milliseconds.
14. **`limitations`**: Explicit lists for missing data, unavailable sensors, processing failures, and model limitations.

---

## 4. Failure, Missing Data & Sensor Availability Semantics

Agni-Netra strictly distinguishes between different operational limitations:

- **UNAVAILABLE SENSOR**: Optional sensors (e.g. Sentinel optical imagery or SAR) being absent does NOT cause pipeline failure. The sensor status is recorded as `UNAVAILABLE`, pipeline status remains `COMPLETE`, and limitations list `"SENTINEL"`.
- **MISSING DATA**: Historical baselines or context data being unavailable is recorded explicitly as missing data (`missing_history_indicator == 1`). Abnormality state becomes `"UNKNOWN"`, and limitations list `"HISTORICAL_BASELINE"`.
- **INSUFFICIENT OBSERVATION**: Events with sparse detection timelines or low observation quality transition gracefully to `decision_state = "INSUFFICIENT_OBSERVATION"`, `pipeline_status = "INSUFFICIENT_OBSERVATION"`, and `verification_state = "INSUFFICIENT_DATA"`.
- **INVALID INPUT**: Malformed or unparseable event inputs trigger an explicit pipeline status `FAILED` with error code `"INVALID_INPUT"`. The pipeline returns a valid structured result containing error details, avoiding unhandled crashes.

---

## 5. Schema Versioning & Downstream Compatibility

- **Schema Version**: `AGN-EVENT-INTELLIGENCE-1.0`
- **Pipeline Version**: `1.0.0`

The structured output is fully JSON-serializable (`to_dict()` / `from_dict()`) and ready for downstream integration with REST API gateways, GIS mapping dashboards, alert subscription engines, and human verification workflows.

---

## 6. Monotonicity & Decoupling Protections

1. **Source Decoupling**: Facility context or Low-T thermal persistence never force source class assignment to `INDUSTRIAL_FIRE`.
2. **Risk vs Priority Separation**: Physical risk ($\text{Hazard} \times \text{Impact}$) and operational response priority remain mathematically and semantically distinct.
3. **No Synthetic Hacks**: No hidden defaults are used to convert missing data into zero risk or safe status.
