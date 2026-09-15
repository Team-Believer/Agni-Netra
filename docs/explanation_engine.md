# Agni-Netra WHY / WHY NOT / WHAT CHANGED Explanation Engine (Phase 17G)

## 1. Executive Summary & Core Principle

The **WHY / WHY NOT / WHAT CHANGED Explanation Engine** converts structured pipeline outputs (canonical features, Low-T persistent heat, historical abnormality, evidence aggregation, confidence/calibration, risk & priority) into deterministic, auditable, and human-readable explanations.

$$\text{EXPLANATION} \neq \text{NEW INFERENCE}$$

### Fundamental Constraints
1. **Evidence Grounded**: Every claim in an explanation is derived strictly from existing structured system outputs. The engine never invents evidence, hallucinate observations, or infer unobserved facts.
2. **Every Claim Has Provenance**: Every major explanation claim maps directly to structured evidence items (`evidence_source_ids`), evidence families (`evidence_family_ids`), or reason codes (`reason_codes`).
3. **Deterministic & Template-Driven**: The engine is **not** a generative LLM chatbot. Given identical structured inputs, it generates identical structured outputs and operator summaries.
4. **Controlled Calibrated Language**: Absolute uncalibrated phrasing ("confirmed fire", "certainly safe", "definitively not a fire") is strictly forbidden unless supported by explicit human verification states.

---

## 2. Core Explanation Structure

```
+-----------------------------------------------------------------------------------+
|                                 INPUT PIPELINE PIPELINE                           |
|  - Canonical Event Features (AGN-FEATURES-1.1)                                    |
|  - Low-T Persistent Heat Result                                                   |
|  - Historical Abnormality & Change Result                                         |
|  - Event Evidence Ledger & Support Matrix                                         |
|  - Decision Assessment & Calibration Status                                       |
|  - Risk & Priority Assessment                                                     |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                             EXPLANATION GENERATOR                                 |
+-----------------------------------------------------------------------------------+
  |                                 |                                 |
  +----------> WHY <----------------+-----> WHY NOT <-----------------+
  |  - Supporting evidence families |  - Competing hypotheses         |
  |  - Strongest independent signals|  - Conflicting evidence families|
  |  - Model-derived attribution    |  - Missing critical evidence    |
  |                                 |                                 |
  +---------> WHAT CHANGED <--------+-----> UNCERTAINTY / LIMITATIONS |
  |  - FRP Spikes / Change points   |  - Evidence completeness score  |
  |  - Footprint expansion          |  - Convergence summary          |
  |  - Baseline historical deviation|  - Decision state reason codes  |
  |                                 |                                 |
  +---------> OPERATIONAL ACTION <--+-----> PROVENANCE <--------------+
     - Priority & Urgency drivers      - evidence_source_ids          |
     - Action recommendations          - evidence_family_ids          |
     - Verification requirements       - reason_codes                 |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        STRUCTURED EVENT EXPLANATION OBJECT                        |
|  - event_id, summary, classification, why, why_not, what_changed,                 |
|    uncertainty, risk_priority, next_action, provenance                            |
+-----------------------------------------------------------------------------------+
```

---

## 3. The 5 Core Questions

### 1. WHY?
Explains the strongest independent evidence supporting the predicted classification.
- Groups evidence by independent family (`THERMAL`, `TEMPORAL`, `SPATIAL`, `SENTINEL`, `CONTEXT`, `BEHAVIOR`, `ANOMALY`, `MODEL`).
- Synthesizes features into meaningful statements (e.g., "Thermal intensity is elevated above detection baseline").
- Labels model outputs explicitly as model-derived (e.g., "Model-derived probability score (0.85) favors INDUSTRIAL_FIRE").

### 2. WHY NOT?
Explains alternative interpretations and evidence limitations:
- Surfaces competing source hypotheses from the support matrix with candidate model scores.
- Lists conflicting evidence items (e.g., "Forest/Vegetation context provides competing interpretation").
- Identifies missing critical evidence items (e.g., "MISSING: Sentinel optical confirmation").

### 3. WHAT CHANGED?
Surfaces historical abnormality and change point indicators:
- FRP thermal intensity spikes.
- Rapid footprint expansion relative to history.
- Activity shifts or regime changes.
- If historical baseline is insufficient (`missing_history_indicator == 1`), explicitly reports: `"Historical baseline is insufficient to establish change or abnormality."`

### 4. UNKNOWN / LIMITATIONS
Surfaces operational uncertainty:
- `INSUFFICIENT_OBSERVATION`: Explains sparse observation history or low data quality.
- `UNKNOWN`: Explains why independent evidence is insufficient to resolve source class.
- `NEEDS_VERIFICATION`: Highlights operational uncertainty and evidence conflict requiring human review.
- `KNOWN`: Summarizes how independent evidence satisfies auto-classification policy.

### 5. WHAT SHOULD HAPPEN NEXT?
Surfaces operational actions from Phase 17F:
- Action recommendations (`IMMEDIATE_REVIEW`, `PRIORITY_REVIEW`, `VERIFY`, `MONITOR`, `INFORMATIONAL`).
- Verification flag (`verification_required: true/false`).

---

## 4. Controlled Phrasing Rules & Decoupling

| Concept | Forbidden Phrasing | Required Calibrated Phrasing |
| :--- | :--- | :--- |
| **Classification** | "Confirmed fire", "Definitely a fire" | "Classified as [CLASS] with [CONFIDENCE] decision confidence" |
| **Facility Context** | "Industrial facility nearby, therefore industrial fire" | "Nearby industrial facility context supports an anthropogenic heat interpretation" |
| **Low-T Behavior** | "Low-T proves industrial fire" | "Persistent low-temperature thermal behavior supports sustained thermal activity" |
| **Model Predictions** | "AI knows this is a wildfire" | "Model-derived probability score (0.85) favors Wildfire" |
| **Safety Assertions** | "Definitively safe", "Certain safe event" | "Current activity remains within normal historical baseline limits" |

---

## 5. Output Contract (`EventExplanation`)

```json
{
  "event_id": "evt_2026_0915_001",
  "summary": "Event evt_2026_0915_001 is classified as INDUSTRIAL_FIRE with HIGH decision confidence (KNOWN).\n\nWhy:\n- Thermal intensity is elevated above detection baseline\n- Event exhibits repeated detections and temporal persistence\n- Sentinel optical imagery corroboration is present\n- Nearby industrial facility context supports an anthropogenic heat interpretation\n- Model-derived probability score (0.85) favors INDUSTRIAL_FIRE\n\nWhy not:\n- No major evidence conflicts observed\n\nWhat changed:\n- Normal historical baseline activity.\n  * Current thermal activity remains within expected historical baseline limits.\n\nRisk & Priority:\n- Physical Risk Level: HIGH (Base Score: 0.72, Risk Confidence: 0.85)\n- Priority Level: P1 (Urgency: HIGH)\n\nAction:\n- Recommended Action: PRIORITY_REVIEW\n- Verification Required: NO\n\nUncertainty & Limitations:\n- Evidence Completeness: 0.85\n- Decision State: KNOWN",
  "classification": {
    "predicted_source_class": "INDUSTRIAL_FIRE",
    "decision_state": "KNOWN"
  },
  "why": {
    "headline": "Event is classified as INDUSTRIAL_FIRE with HIGH decision confidence supported by CONTEXT, SENTINEL, TEMPORAL, THERMAL evidence.",
    "supporting_families": ["CONTEXT", "SENTINEL", "TEMPORAL", "THERMAL"],
    "supporting_reasons": [
      "Thermal intensity is elevated above detection baseline",
      "Event exhibits repeated detections and temporal persistence",
      "Sentinel optical imagery corroboration is present",
      "Nearby industrial facility context supports an anthropogenic heat interpretation",
      "Model-derived probability score (0.85) favors INDUSTRIAL_FIRE"
    ]
  },
  "why_not": {
    "competing_hypotheses": ["ROUTINE_FLARE (competing model score = 0.10)", "WILDFIRE (competing model score = 0.10)"],
    "conflicting_families": [],
    "limiting_reasons": []
  },
  "what_changed": {
    "change_detected": false,
    "change_reasons": ["Current thermal activity remains within expected historical baseline limits."],
    "historical_comparison": "Normal historical baseline activity."
  },
  "uncertainty": {
    "confidence_level": "HIGH",
    "evidence_completeness": 0.85,
    "evidence_convergence": 1.0,
    "uncertainty_reasons": [],
    "missing_information": []
  },
  "risk_priority": {
    "risk_level": "HIGH",
    "risk_confidence": 0.85,
    "priority_level": "P1",
    "urgency": "HIGH",
    "operational_action": "PRIORITY_REVIEW",
    "priority_drivers": ["CRITICAL_FACILITY_PROXIMITY", "HIGH_HAZARD", "HIGH_IMPACT_CONTEXT"]
  },
  "next_action": {
    "recommendation": "PRIORITY_REVIEW",
    "verification_required": false
  },
  "provenance": {
    "evidence_source_ids": ["f6984e1b-4d40-41a4-9dfc-2795c7ef7f41"],
    "evidence_family_ids": ["CONTEXT", "FACILITY", "SENTINEL", "TEMPORAL", "THERMAL"],
    "reason_codes": ["CRITICAL_FACILITY_PROXIMITY", "HIGH_HAZARD", "HIGH_IMPACT_CONTEXT"]
  }
}
```
