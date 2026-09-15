# Agni-Netra Confidence Calibration & Unknown Decision Engine (Phase 17E)

## 1. Overview & Architecture

The **Confidence Calibration & Unknown Decision Engine** is Agni-Netra's production layer for calibrating classifier probabilities, evaluating multi-dimensional evidence quality, and determining explicit operational decision states.

It enforces the foundational system principle:
$$\text{Prediction} \neq \text{Confidence} \neq \text{Evidence Completeness} \neq \text{Risk}$$

High model classifier output alone is **never** permitted to bypass evidence quality or observation sufficiency gates.

```
+-----------------------------------------------------------------------+
|                           INPUT EVIDENCE                              |
|  - Raw Model Probabilities  - Event Evidence Ledger                   |
|  - Canonical Event Features - Low-T Persistent Heat Result            |
|  - Historical Abnormality   - Data Quality / Observation Quality      |
+-----------------------------------------------------------------------+
                                  |
                                  v
+-----------------------------------------------------------------------+
|                    CONFIDENCE CALIBRATION LAYER                       |
|  - Pluggable Calibrator (Temperature, Isotonic, Identity Fallback)    |
|  - Explicit Status (CALIBRATED, FALLBACK, UNCALIBRATED)               |
+-----------------------------------------------------------------------+
                                  |
                                  v
+-----------------------------------------------------------------------+
|                    MULTI-DIMENSIONAL ASSESSMENT                       |
|  - Classification Confidence   - Evidence Completeness                |
|  - Evidence Convergence        - Data Quality Confidence              |
|  - Temporal Sufficiency        - Historical Sufficiency               |
|  - Contradiction Penalty                                              |
+-----------------------------------------------------------------------+
                                  |
                                  v
+-----------------------------------------------------------------------+
|                     ABSTENTION DECISION HIERARCHY                     |
|  1. INSUFFICIENT_OBSERVATION (Poor quality or sparse time-series)     |
|  2. UNKNOWN                  (Ambiguous/missing evidence support)     |
|  3. NEEDS_VERIFICATION       (Conflict or operational uncertainty)    |
|  4. KNOWN                    (Satisfies all quality/evidence gates)   |
+-----------------------------------------------------------------------+
                                  |
                                  v
+-----------------------------------------------------------------------+
|                    DECISION ASSESSMENT CONTRACT                       |
|  - event_id                  - predicted_source_class                 |
|  - decision_state            - confidence & calibration details       |
|  - evidence_summary          - abstention reasons & limiting factors  |
|  - operational_action (AUTO_CLASSIFY / REVIEW / VERIFY / INSUFFICIENT) |
+-----------------------------------------------------------------------+
```

---

## 2. Separately Inspectable Confidence Dimensions

The engine evaluates distinct dimensions rather than blindly multiplying values into a single scalar:

1. **Classification Confidence ($C_{\text{class}}$)**: Calibrated (or fallback) probability from the classifier for the predicted source class.
2. **Evidence Completeness ($E_{\text{comp}}$)**: Fraction of expected evidence families present with non-missing observations ($0.0 \dots 1.0$).
3. **Evidence Convergence ($E_{\text{conv}}$)**: Degree of agreement across independent evidence families ($0.0 \dots 1.0$). Evaluated by family independence, not simple feature counting.
4. **Data Quality Confidence ($Q_{\text{data}}$)**: Reliability of underlying observations ($0.0 \dots 1.0$).
5. **Temporal Sufficiency ($S_{\text{temp}}$)**: Adequacy of detection count, duration, and continuity ($0.0 \dots 1.0$).
6. **Historical Sufficiency ($S_{\text{hist}}$)**: Availability and quality of historical baselines for change analysis ($0.0 \dots 1.0$).
7. **Contradiction Penalty ($P_{\text{contra}}$)**: Penalty assigned due to conflicting evidence families ($0.0 \dots 1.0$).

Overall decision confidence is calculated via auditable score composition:
$$C_{\text{decision}} = \text{max}\left(0, \text{min}\left(1, 0.35 C_{\text{class}} + 0.25 E_{\text{comp}} + 0.25 E_{\text{conv}} + 0.15 Q_{\text{data}} - 0.30 P_{\text{contra}}\right)\right)$$

Confidence Levels:
- $\ge 0.85$: `VERY_HIGH`
- $\ge 0.70$: `HIGH`
- $\ge 0.50$: `MODERATE`
- $\ge 0.30$: `LOW`
- $< 0.30$: `VERY_LOW`

---

## 3. Calibration Abstraction & Fallback

Raw classifier probabilities are wrapped in the pluggable `ConfidenceCalibrator` interface.

### Supported Methods
- **Temperature Scaling (`temperature`)**: Applies temperature factor $T > 0$ on logit scale.
- **Isotonic Scaling (`isotonic`)**: Interpolates calibrated values using piecewise linear curves.
- **Identity Fallback (`identity`)**: Passes raw confidence unchanged when no calibration dataset or parameters are supplied.
- **Unavailable (`unavailable`)**: Marks calibration as explicitly unavailable.

### Explicit Metadata Tracking
Every output records calibration provenance explicitly:
- `calibration_status`: `CALIBRATED`, `FALLBACK`, `UNCALIBRATED`
- `calibration_method`: `temperature`, `isotonic`, `identity`, `unavailable`

> **CRITICAL RULE**: Raw model probability is NOT calibrated confidence. When no calibration mapping is supplied, the engine explicitly reports status `FALLBACK` or `UNCALIBRATED`.

---

## 4. Abstention Hierarchy & Decision States

Agni-Netra treats `UNKNOWN` as a **valid product outcome**, not a system failure.

The abstention hierarchy is evaluated in strict sequential priority:

```
  +-------------------------------------------------------------+
  |              1. INSUFFICIENT_OBSERVATION                    |
  |  Trigger: Low data quality (< 0.4) or insufficient temporal |
  |  or historical observations. Action: INSUFFICIENT_DATA       |
  +-------------------------------------------------------------+
                                 | No
                                 v
  +-------------------------------------------------------------+
  |                      2. UNKNOWN                             |
  |  Trigger: Low completeness (< 0.4), weak convergence,       |
  |  no supporting families, or raw prob < 0.35.                |
  |  Action: REVIEW_RECOMMENDED                                 |
  +-------------------------------------------------------------+
                                 | No
                                 v
  +-------------------------------------------------------------+
  |                 3. NEEDS_VERIFICATION                       |
  |  Trigger: Conflicting evidence, moderate model uncertainty, |
  |  or decision confidence < 0.65. Action: VERIFY_REQUIRED     |
  +-------------------------------------------------------------+
                                 | No
                                 v
  +-------------------------------------------------------------+
  |                       4. KNOWN                              |
  |  Trigger: Satisfies all quality and evidence gates.          |
  |  Action: AUTO_CLASSIFY                                      |
  +-------------------------------------------------------------+
```

---

## 5. Machine-Readable Reason Codes

When an event is abstained (`INSUFFICIENT_OBSERVATION`, `UNKNOWN`, or `NEEDS_VERIFICATION`), explicit machine-readable codes are emitted:

- `INSUFFICIENT_TEMPORAL_HISTORY`: Sparse time-series or single detection.
- `INSUFFICIENT_HISTORICAL_BASELINE`: Missing baseline for change scoring.
- `LOW_EVIDENCE_COMPLETENESS`: Missing critical sensor or context inputs.
- `LOW_INDEPENDENT_CONVERGENCE`: Supporting evidence does not span independent families.
- `STRONG_EVIDENCE_CONFLICT`: Conflicting evidence observed (e.g. vegetation vs industrial context).
- `LOW_DATA_QUALITY`: Low observation quality score.
- `SOURCE_AMBIGUITY`: Ambiguous source characteristics across candidate classes.
- `MODEL_UNCERTAINTY`: Low classifier output.
- `CRITICAL_EVIDENCE_MISSING`: Sentinel optical or context evidence missing.

---

## 6. Centralized Configuration & Thresholds

All policy parameters are centralized in `ConfidenceEngineConfig`:

```python
@dataclass
class ConfidenceEngineConfig:
    min_data_quality: float = 0.4
    min_temporal_sufficiency: float = 0.3
    min_historical_sufficiency: float = 0.3
    min_evidence_completeness: float = 0.4
    min_evidence_convergence: float = 0.4
    min_model_confidence_known: float = 0.60
    min_decision_confidence_known: float = 0.65
    max_contradiction_penalty_known: float = 0.25
    max_contradiction_penalty_verification: float = 0.50
```

---

## 7. Evidence Conflict & Family-Aware Convergence

- **Missing Evidence $\neq$ Conflicting Evidence**: Missing evidence (e.g., unavailable Sentinel imagery) lowers `evidence_completeness` but does NOT increase `contradiction_penalty`.
- **Family Independence**: Multiple items within the same family (e.g., three thermal FRP detections) count toward that single family (`THERMAL`). Convergence requires agreement across multiple distinct families (`THERMAL`, `TEMPORAL`, `CONTEXT`, `SENTINEL`, `ANOMALY`).

---

## 8. Source-Agnostic Operation & Decoupling

Agni-Netra supports cross-class decision making across:
- `INDUSTRIAL_FIRE`
- `ROUTINE_FLARE`
- `ABNORMAL_EMERGENCY_FLARE`
- `WILDFIRE`
- `AGRICULTURAL_BURN`
- `MINING_INDUSTRIAL_HEAT`
- `LANDFILL_OTHER_ANTHROPOGENIC`
- `OTHER`
- `UNKNOWN`

Decoupling Enforcement:
- Facility context is supporting evidence only, and cannot independently force `INDUSTRIAL_FIRE`.
- Low-T thermal persistence is a behavioral signal, and cannot independently force `INDUSTRIAL_FIRE`.

---

## 9. Output Contract (`DecisionAssessment`)

```json
{
  "event_id": "evt_2026_0915_001",
  "predicted_source_class": "INDUSTRIAL_FIRE",
  "decision_state": "NEEDS_VERIFICATION",
  "confidence": {
    "classification_confidence": 0.85,
    "evidence_completeness": 0.75,
    "evidence_convergence": 0.60,
    "data_quality_confidence": 0.90,
    "temporal_sufficiency": 1.0,
    "historical_sufficiency": 1.0,
    "contradiction_penalty": 0.35,
    "overall_decision_confidence": 0.64,
    "confidence_level": "MODERATE",
    "decision_state": "NEEDS_VERIFICATION",
    "abstention_reason": ["STRONG_EVIDENCE_CONFLICT"],
    "limiting_factors": ["Evidence contradiction detected in families: ['CONTEXT']"],
    "evidence_family_summary": {
      "supporting_families": ["ANOMALY", "BEHAVIOR", "TEMPORAL", "THERMAL"],
      "conflicting_families": ["CONTEXT"],
      "missing_critical_families": ["SENTINEL"],
      "net_supporting_count": 3
    }
  },
  "calibration": {
    "calibration_status": "FALLBACK",
    "calibration_method": "identity",
    "raw_model_confidence": "0.85",
    "calibrated_confidence": "0.85"
  },
  "evidence_summary": {
    "supporting_families": ["ANOMALY", "BEHAVIOR", "TEMPORAL", "THERMAL"],
    "conflicting_families": ["CONTEXT"],
    "missing_critical_families": ["SENTINEL"],
    "convergence_summary": "4 supporting, 1 conflicting"
  },
  "abstention": {
    "is_abstained": true,
    "abstention_reason_codes": ["STRONG_EVIDENCE_CONFLICT"],
    "limiting_factors": ["Evidence contradiction detected in families: ['CONTEXT']"]
  },
  "operational_action": "VERIFY_REQUIRED"
}
```

---

## 10. Real-World Safety & Important Limitations

1. **Safety Claims**: Agni-Netra does NOT issue non-qualified absolute assertions such as "confirmed fire" or "definitively safe". Operational decisions use qualified language ("classified as", "likely", "evidence supports", "verification required").
2. **Empirical Calibration**: Calibration parameters require validation against domain-specific empirical calibration datasets before asserting status `CALIBRATED`.
