# Agni-Netra AI/ML Output Contract & Handoff Freeze

> [!IMPORTANT]
> **THIS IS THE OFFICIAL AI/ML OUTPUT CONTRACT (Schema `AGN-EVENT-INTELLIGENCE-1.0`).**
> Separate backend, REST API, database, and frontend UI layers MUST consume this contract directly rather than re-implementing or re-inferring ML logic.

---

## Executive Overview

This document specifies the frozen interface contract for the Agni-Netra AI/ML intelligence engine produced by `analyze_event()`.

- **Schema Version**: `AGN-EVENT-INTELLIGENCE-1.0`
- **Pipeline Version**: `1.0.0`
- **Determinism Guarantee**: Identical input observation payloads produce byte-for-byte identical decision, assessment, risk, and explanation outputs.
- **Serialization Standard**: ISO-8601 timestamps, standard JSON primitives (`str`, `int`, `float`, `bool`, `list`, `dict`), zero unhandled `NaN`/`Infinity` floats, full round-trip `from_dict(to_dict())` support.

---

## 1. Top-Level Canonical Contract Structure (16 Sections)

The top-level `EventIntelligenceResult` JSON object exposes exactly 16 self-contained, versioned sections:

```json
{
  "schema_version": "AGN-EVENT-INTELLIGENCE-1.0",
  "pipeline_version": "1.0.0",
  "event": { ... },
  "observation": { ... },
  "thermal": { ... },
  "behavior": { ... },
  "abnormality": { ... },
  "source": { ... },
  "novelty": { ... },
  "evidence": { ... },
  "confidence": { ... },
  "risk": { ... },
  "priority": { ... },
  "explanation": { ... },
  "verification": { ... },
  "pipeline": { ... },
  "limitations": { ... },
  "provenance": { ... }
}
```

---

## 2. Detailed Section Specifications

### Section 1: `event` (Event Metadata & Identity)
- `event_id` (str): Persistent unique identifier (e.g. `"AGN-E-000421"`).
- `first_observation_time` (str): ISO-8601 timestamp of earliest observation.
- `last_observation_time` (str): ISO-8601 timestamp of latest observation.
- `latitude` (float): Spatial centroid latitude in decimal degrees WGS-84.
- `longitude` (float): Spatial centroid longitude in decimal degrees WGS-84.
- `observation_count` (int): Total number of associated satellite observations.
- `source_sensor_summary` (str): Primary sensing instruments (e.g. `"FIRMS_VIIRS"`).

### Section 2: `observation` (Data Quality & Saturation Defense)
- `quality_summary` (str): Human-readable quality statement.
- `usable_observations` (int): Number of valid, uncorrupted observations.
- `degraded_observations` (int): Observations flagged with downweighted quality.
- `excluded_observations` (int): Observations excluded due to fatal corruption.
- `sensor_availability` (dict): Sensor pass status (`sentinel_available`, `insat3ds_available`).
- `freshness` (str): Latency indicator (`REALTIME`, `RECENT`, `HISTORICAL`).

### Section 3: `thermal` (Multi-Lane Physics)
- `low_t` (dict): Low-T persistent heat status, persistence score, spatial stability.
- `high_t` (dict): High-T physics mode, thermal intensity score, high-T likelihood, saturation state.
- `frp_summary` (dict): `max_frp` (MW) and `frp_stability`.
- `brightness_temperature_summary` (dict): `t4_max` (K) and `t11_max` (K).
- `thermal_limitations` (list[str]): Physical limitations or missing spectral bands.

### Section 4: `behavior` (Event State Machine)
- `event_state` (str): Frozen behavioral state (`NEW`, `PERSISTING`, `STABLE`, `INTERMITTENT`, `ESCALATING`, `ABNORMAL`, `RESOLVING`, `DORMANT`, `REACTIVATED`, `UNKNOWN`).
- `state_confidence` (float): State classification confidence [0.0, 1.0].
- `state_history` (list[str]): Chronological sequence of states.
- `transition` (dict): `last_transition` and `reason_codes`.
- `low_t_behavior` (str): `LOW_T_PERSISTENT` or `TRANSIENT_OR_DEVELOPING`.
- `high_t_behavior` (str): `HIGH_TEMPERATURE_FLARE_LIKE`, `MODERATE_THERMAL`, etc.

### Section 5: `abnormality` (Historical Baseline & Change)
- `abnormality_score` (float): Deviation score relative to multi-year facility baseline [0.0, 1.0].
- `abnormality_level` (str): `NORMAL`, `UNUSUAL`, `HIGHLY_ABNORMAL`, `UNKNOWN`.
- `change_detected` (bool): True if sudden change or deviation point detected.
- `change_summary` (list[str]): Auditable change descriptions.
- `history_tier` (str): `LONG_TERM_BASELINE`, `SPARSE_HISTORY`, `NO_HISTORY`.
- `baseline_sufficiency` (float): Baseline data sufficiency score [0.0, 1.0].

### Section 6: `source` (Source Intelligence & Model Prediction)
- `predicted_source_class` (str): Frozen source class (`INDUSTRIAL_FIRE`, `ROUTINE_FLARE`, `ABNORMAL_EMERGENCY_FLARE`, `WILDFIRE`, `AGRICULTURAL_BURN`, `MINING_INDUSTRIAL_HEAT`, `LANDFILL_OTHER_ANTHROPOGENIC`, `OTHER`, `UNKNOWN`).
- `decision_state` (str): Frozen decision state (`KNOWN`, `UNKNOWN`, `NEEDS_VERIFICATION`, `INSUFFICIENT_OBSERVATION`).
- `model_confidence` (float): Gated classification confidence score [0.0, 1.0].
- `model_prediction` (dict): Raw model class probabilities.
- `known_class_compatibility` (list[dict]): Non-calibrated compatibility metrics per class.

### Section 7: `novelty` (Out-Of-Distribution Intelligence)
- `novelty_score` (float): Multi-signal novelty score [0.0, 1.0].
- `novelty_level` (str): `KNOWN_LIKE`, `LOW_NOVELTY`, `MODERATE_NOVELTY`, `HIGH_NOVELTY`, `NOVEL`, `UNKNOWN`.
- `distribution_state` (str): `KNOWN_LIKE`, `NOVEL`, `UNKNOWN`.
- `novelty_drivers` (list[str]): Explicit reason codes for novelty (e.g. `FEATURE_SPACE_DEVIATION`, `HIGH_CONFIDENCE_OOD`).

### Section 8: `evidence` (Event Evidence Ledger)
- `ledger` (dict): Full evidence ledger containing `evidence_items`.
- `supporting_families` (list[str]): Evidence family IDs providing supporting evidence.
- `conflicting_families` (list[str]): Evidence family IDs providing conflicting evidence.
- `missing_families` (list[str]): Missing sensor/data evidence families.
- `neutral_families` (list[str]): Neutral evidence families.
- `evidence_strength` (str): `WEAK`, `MODERATE`, `STRONG`, `VERY_STRONG`.
- `evidence_completeness` (float): Global completeness score [0.0, 1.0].
- `evidence_convergence` (str): `HIGH`, `MODERATE`, `LOW`, `CONTRADICTORY`.
- `hypothesis_support_matrix` (dict): Per-class evidence support breakdowns.

### Section 9: `confidence` (Calibration & Abstention Gating)
- `classification_confidence` (float): Model confidence score.
- `evidence_completeness` (float): Completeness factor.
- `evidence_convergence` (float): Convergence factor.
- `data_quality_confidence` (float): Observation quality factor.
- `temporal_sufficiency` (float): Temporal observation adequacy score.
- `historical_sufficiency` (float): Historical baseline adequacy score.
- `contradiction_penalty` (float): Penalty applied for conflicting evidence.
- `overall_decision_confidence` (float): Calibrated overall decision confidence [0.0, 1.0].
- `confidence_level` (str): `VERY_HIGH`, `HIGH`, `MODERATE`, `LOW`, `VERY_LOW`.
- `calibration_status` (str): `CALIBRATED` or `UNCALIBRATED`.
- `calibration_method` (str): Calibration technique used (e.g. `TEMPERATURE_SCALING`).
- `abstention_reason_codes` (list[str]): Reasons triggering safe abstention.
- `limiting_factors` (list[str]): Critical limiting factors.

### Section 10: `risk` (Risk Intelligence)
- `hazard_score` (float): Physical thermal hazard score [0.0, 1.0].
- `hazard_level` (str): `NEGLIGIBLE`, `LOW`, `MODERATE`, `HIGH`, `CRITICAL`.
- `impact_score` (float): Contextual facility/population impact score [0.0, 1.0].
- `impact_level` (str): `NEGLIGIBLE`, `LOW`, `MODERATE`, `HIGH`, `CRITICAL`.
- `base_risk_score` (float): Combined risk score [0.0, 1.0].
- `risk_level` (str): Frozen risk level (`NEGLIGIBLE`, `LOW`, `MODERATE`, `HIGH`, `CRITICAL`, `UNKNOWN`).
- `risk_confidence` (float): Confidence in risk assessment [0.0, 1.0].

### Section 11: `priority` (Operational Urgency & Action)
- `priority_score` (float): Operational priority score [0.0, 1.0].
- `priority_level` (str): Frozen priority level (`P4_ROUTINE`, `P3_MONITOR`, `P2_EVALUATE`, `P1_URGENT`, `P0_CRITICAL`, `UNKNOWN`).
- `urgency` (str): Frozen urgency level (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`, `IMMEDIATE`, `UNKNOWN`).
- `operational_action` (str): Recommended operational response (`INFORMATIONAL`, `MONITOR`, `VERIFY`, `INSPECT_URGENT`, `EMERGENCY_RESPONSE`).
- `priority_drivers` (list[str]): Auditable priority driver reason codes.

### Section 12: `explanation` (WHY / WHY NOT / WHAT CHANGED)
- `summary` (str): Concise 1-2 sentence evidence-grounded summary statement.
- `why` (dict): Primary supporting evidence & reason statements.
- `why_not` (dict): Excluded source classes with explicit rejection rationale.
- `what_changed` (dict): Temporal baseline change and escalation summary.
- `uncertainty` (dict): Limiting factors, missing evidence, and decision uncertainty.
- `next_action` (dict): Recommended operational action and verification flag.
- `provenance` (dict): Provenance mapping linking statements back to evidence items.

### Section 13: `verification` (Human Verification & Workflow State)
- `verification_state` (str): Frozen state (`NOT_REQUIRED`, `VERIFY_REQUIRED`, `REVIEW_RECOMMENDED`, `INSUFFICIENT_DATA`, `HUMAN_VERIFIED`, `HUMAN_DISPUTED`).
- `verification_required` (bool): True if human verification is required before operational dispatch.
- `verification_reason` (str): Reason for verification state assignment.

### Section 14: `pipeline` (Execution Status & Audit Traces)
- `schema_version` (str): `AGN-EVENT-INTELLIGENCE-1.0`.
- `pipeline_version` (str): `1.0.0`.
- `overall_status` (str): `COMPLETE`, `PARTIAL`, `INSUFFICIENT_OBSERVATION`, `FAILED`.
- `stage_status` (dict): Status per stage (`PASSED`, `PARTIAL`, `SKIPPED`, `FAILED`).
- `stage_durations_if_available` (dict): Execution latency per stage in milliseconds.
- `warnings` (list[str]): Non-fatal execution warnings.

### Section 15: `limitations` (Explicit Data & Model Boundaries)
- `missing_data` (list[str]): Explicit missing inputs (e.g. `["missing_history"]`).
- `unavailable_sensors` (list[str]): Unavailable sensor channels (e.g. `["SENTINEL", "SAR"]`).
- `insufficient_history` (bool): True if historical baseline is insufficient.
- `quality_limitations` (list[str]): Observation quality flags.
- `model_limitations` (list[str]): Model domain boundaries.
- `confidence_limitations` (list[str]): Factors reducing decision confidence.

### Section 16: `provenance` (Complete Evidence Traceability)
- `observation_ids` (list[str]): Source observation IDs.
- `event_id` (str): Unique event ID.
- `evidence_source_ids` (list[str]): Source evidence IDs in ledger.
- `evidence_family_ids` (list[str]): Active evidence family IDs.
- `reason_codes` (list[str]): Combined machine-readable reason codes.

---

## 3. Mandatory Semantic Separation Rules

Downstream systems must maintain the following architectural boundaries:

1. `SOURCE != EVENT_STATE`: Source identity (`WILDFIRE`) is distinct from behavioral state (`PERSISTING`).
2. `EVENT_STATE != ABNORMALITY`: Low-T persistence or temporal stability is decoupled from baseline abnormality.
3. `ABNORMALITY != NOVELTY`: Historical baseline shifts do not automatically imply out-of-distribution archetype novelty.
4. `NOVELTY != DECISION_STATE`: Distribution state (`NOVEL`) is separate from decision state (`NEEDS_VERIFICATION`).
5. `MODEL_CONFIDENCE != DECISION_CONFIDENCE`: Raw model output probabilities are distinct from overall decision confidence.
6. `EVIDENCE_COMPLETENESS != CONFIDENCE`: Having complete observations does not guarantee high confidence if evidence conflicts.
7. `CONFIDENCE != RISK`: Low confidence does not imply low physical risk.
8. `RISK != PRIORITY`: Priority scales with operational urgency and context, not raw hazard alone.
9. `LOW_T != SOURCE` & `HIGH-T != SOURCE`: Thermal intensity physics does not dictate source classification directly.
10. `INSAT3DS != GROUND_TRUTH`: High-cadence GEO thermal observations provide temporal continuity but do not represent gold-standard ground truth.
11. `UNKNOWN != FAILURE`: `UNKNOWN` is a valid, safe abstention state when evidence is insufficient or contradictory.
12. `INSUFFICIENT_OBSERVATION != UNKNOWN`: Sparse data triggers `INSUFFICIENT_OBSERVATION`, whereas conflicting data triggers `UNKNOWN` or `NEEDS_VERIFICATION`.

---

## 4. Representative Handoff Example

A complete representative handoff JSON payload is stored at:
[`docs/examples/event_intelligence_example.json`](file:///C:/Users/NIrmit/Desktop/Agni-Netra/Agni-Netra/docs/examples/event_intelligence_example.json)

---

## 5. Contract Validator Usage

The AI layer provides a lightweight contract validator (`src/intelligence/output_contract.py`):

```python
from src.intelligence.output_contract import validate_event_intelligence_result

# Validate any EventIntelligenceResult instance or dictionary payload
errors = validate_event_intelligence_result(result)
if len(errors) == 0:
    print("Contract validation PASSED: Schema AGN-EVENT-INTELLIGENCE-1.0 compliant.")
else:
    for err in errors:
        print(f"Validation Error [{err.section} -> {err.field}]: {err.message}")
```
