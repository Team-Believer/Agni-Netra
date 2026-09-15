# Agni-Netra Risk & Priority Intelligence Engine (Phase 17F)

## 1. Executive Summary & Core Principles

The **Risk & Priority Intelligence Engine** converts multi-source thermal event evidence, canonical features, historical abnormality, Low-T behavior, and decision confidence into calibrated **Physical Risk** and **Operational Priority** assessments.

It strictly enforces Agni-Netra's foundational product principles:

$$\text{Source} \neq \text{Behavior} \neq \text{Abnormality} \neq \text{Evidence} \neq \text{Confidence} \neq \text{Severity} \neq \text{Impact} \neq \text{Risk} \neq \text{Priority}$$

### Crucial Product Rules
- **RISK $\neq$ PRIORITY**: A high-risk stable routine flare may have low response priority ($P3/P4$), while a low-risk unresolved event near sensitive context may require immediate verification priority ($P1/P0$).
- **CONFIDENCE $\neq$ RISK**: High classifier probability does not create physical hazard. Low classifier probability does not extinguish physical hazard.
- **UNKNOWN $\neq$ ZERO RISK**: Unresolved source class interpretation is an evidence limitation, not a guarantee of safety ($0.0$).
- **FACILITY CONTEXT $\neq$ INDUSTRIAL FIRE**: Industrial proximity increases exposure/impact, but never forces source class assignment.

---

## 2. Architecture & Data Flow

```
+-----------------------------------------------------------------------------------+
|                                 INPUT EVIDENCE                                    |
|  - Canonical Event Features (AGN-FEATURES-1.1)                                    |
|  - Low-T Persistent Heat Result                                                   |
|  - Historical Abnormality & Change Indicators                                     |
|  - Event Evidence Ledger                                                          |
|  - Decision Assessment & Calibration (Phase 17E)                                  |
+-----------------------------------------------------------------------------------+
                                          |
                     +--------------------+--------------------+
                     |                                         |
                     v                                         v
+------------------------------------------+ +------------------------------------------+
|             HAZARD ENGINE                | |              IMPACT ENGINE               |
|  - Source Class Base Hazard              | |  - Proximity to Industrial Facilities  |
|  - FRP Intensity & Change Rate           | |  - Infrastructure & Land Context       |
|  - Spatial Extent & Growth               | |  - Spatial Footprint Extent             |
|  - Abnormality & Persistence             | |  - Explicit Missing Context Handling   |
+------------------------------------------+ +------------------------------------------+
                     |                                         |
                     +--------------------+--------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                                 BASE RISK MODEL                                   |
|                          BASE_RISK = sqrt(HAZARD * IMPACT)                        |
|  - Monotonic & Sanity Bounded                                                     |
|  - Risk Level (VERY_LOW, LOW, MODERATE, HIGH, VERY_HIGH)                          |
+-----------------------------------------------------------------------------------+
                                          |
            +-----------------------------+-----------------------------+
            |                                                           |
            v                                                           v
+---------------------------------------+   +---------------------------------------+
|            URGENCY MODEL              |   |          RISK CONFIDENCE LAYER        |
|  - FRP Spike / Rapid Expansion        |   |  - Derived from Phase 17E Ledger      |
|  - Emergency Flare Signals            |   |  - Decoupled from Class Confidence    |
|  - Decision Verification Need         |   |  - Conflict lowers confidence, not    |
|  - Levels: URGENT, HIGH, NORMAL, LOW  |   |    physical hazard                    |
+---------------------------------------+   +---------------------------------------+
            |                                                           |
            +-----------------------------+-----------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                             OPERATIONAL PRIORITY ENGINE                           |
|      Priority = 0.45 * Base_Risk + 0.30 * Urgency + 0.15 * Impact + 0.10 * Verification |
|  - Levels: P0 (CRITICAL), P1 (HIGH), P2 (MODERATE), P3 (LOW), P4 (INFORMATIONAL)   |
|  - Machine-Readable Priority Drivers & Operational Action Recommendations        |
+-----------------------------------------------------------------------------------+
```

---

## 3. Physical Hazard Model

Hazard evaluates the inherent physical severity and thermal dynamics of the event.

### Baseline Inherent Source Hazard
- `ABNORMAL_EMERGENCY_FLARE`: $0.75$
- `INDUSTRIAL_FIRE`: $0.70$
- `WILDFIRE`: $0.65$
- `LANDFILL_OTHER_ANTHROPOGENIC`: $0.45$
- `AGRICULTURAL_BURN`: $0.35$
- `MINING_INDUSTRIAL_HEAT`: $0.30$
- `ROUTINE_FLARE`: $0.25$
- `OTHER`: $0.30$
- `UNKNOWN`: $0.40$ (Bounded unresolved baseline)

### Physical Modifiers
- **FRP Intensity**: $+0.10$ for FRP $>50$, $+0.20$ for FRP $>100$, $+0.30$ for FRP $>200$ MW.
- **Rapid FRP Increase**: $+0.10$ if FRP change rate $> 2.0$.
- **Spatial Growth**: $+0.10$ if footprint expansion $> 1.5$.
- **Historical Abnormality**: $+0.15 \times \text{abnormality\_score}$.
- **Thermal Persistence**: $+0.05$ if Low-T persistent heat behavior is observed.

---

## 4. Impact & Exposure Model

Impact models consequence and spatial vulnerability:
- **Industrial Infrastructure Proximity**: Base score $0.70$.
- **Commercial/Industrial Land Context**: Base score $0.55$.
- **Vegetation / Remote Context**: Base score $0.30$.
- **Spatial Extent Modifier**: $+0.10$ if spatial footprint $> 2.0$ km².
- **Missing Context Handling**: If facility/context data is missing (`missing_context_indicator == 1`), sets impact to bounded baseline $0.35$, marks `missing_context = True` in output limitations, and records explicit drivers.

---

## 5. Base Risk & Risk Confidence

Base Risk is computed via multiplicative combination:
$$\text{Base Risk} = \sqrt{\text{Hazard} \times \text{Impact}}$$

### Monotonicity Properties
- Increasing hazard with unchanged impact $\implies$ Base risk never decreases.
- Increasing impact with unchanged hazard $\implies$ Base risk never decreases.

### Risk Confidence
- Evaluated independently from classification confidence ($C_{\text{class}}$).
- Captures overall evidence quality, completeness, and convergence.
- **Evidence Conflict Rule**: Evidence conflict lowers `risk_confidence` and flags verification need, but does NOT artificially suppress physical hazard or base risk.

---

## 6. Urgency & Operational Priority (P0 - P4)

Urgency reflects immediate operational dynamics:
- `URGENT`: Rapid FRP spike, emergency flare signal.
- `HIGH`: Rapid footprint expansion, decision state `NEEDS_VERIFICATION`.
- `NORMAL`: Standard continuous detection timeline.
- `LOW`: Routine, highly persistent, low-intensity detection.

### Priority Formulation
$$\text{Priority Score} = 0.45 \times \text{Base Risk} + 0.30 \times \text{Urgency Weight} + 0.15 \times \text{Impact} + 0.10 \times \text{Verification Need}$$

### Priority Levels & Actions
| Priority Level | Description | Action Recommendation |
| :--- | :--- | :--- |
| **P0** ($\ge 0.85$) | Critical / Immediate Attention | `IMMEDIATE_REVIEW` |
| **P1** ($\ge 0.70$) | High Priority | `PRIORITY_REVIEW` |
| **P2** ($\ge 0.50$) | Moderate Priority | `VERIFY` |
| **P3** ($\ge 0.30$) | Low Priority | `MONITOR` |
| **P4** ($< 0.30$) | Informational / Monitor | `INFORMATIONAL` |

---

## 7. Machine-Readable Reason Codes

- `HIGH_HAZARD`: Physical hazard score $\ge 0.70$.
- `HIGH_IMPACT_CONTEXT`: Consequence score $\ge 0.70$.
- `RAPID_THERMAL_INCREASE`: Sudden FRP trend / spike.
- `ABNORMAL_CHANGE_DETECTED`: Historical change or deviation detected.
- `PERSISTENT_ACTIVITY`: Low-T persistent thermal behavior.
- `EMERGENCY_FLARE_SIGNAL`: Candidate abnormal/emergency flare.
- `CRITICAL_FACILITY_PROXIMITY`: Direct proximity to industrial facility.
- `HIGH_EXPOSURE_CONTEXT`: High density or sensitive context.
- `VERIFICATION_REQUIRED`: Unresolved evidence conflict or decision uncertainty.
- `STRONG_EVIDENCE_CONFLICT`: Contradictory evidence families observed.
- `LOW_CONFIDENCE`: Decision confidence below auto-classification threshold.
- `INSUFFICIENT_OBSERVATION`: Observation count/quality insufficient for definitive scoring.

---

## 8. Output Contract (`RiskPriorityAssessment`)

```json
{
  "event_id": "evt_2026_0915_999",
  "risk": {
    "hazard_score": 0.75,
    "hazard_level": "HIGH",
    "impact_score": 0.70,
    "impact_level": "HIGH",
    "base_risk_score": 0.725,
    "risk_level": "HIGH",
    "risk_confidence": 0.82
  },
  "priority": {
    "priority_score": 0.768,
    "priority_level": "P1",
    "urgency": "HIGH",
    "operational_action": "PRIORITY_REVIEW"
  },
  "drivers": {
    "hazard_drivers": [
      "Source class 'INDUSTRIAL_FIRE' base hazard factor (0.70)",
      "Moderate FRP intensity (50.0 MW)"
    ],
    "impact_drivers": [
      "Proximity to critical industrial facility infrastructure"
    ],
    "priority_drivers": [
      "CRITICAL_FACILITY_PROXIMITY",
      "HIGH_HAZARD",
      "HIGH_IMPACT_CONTEXT",
      "PERSISTENT_ACTIVITY"
    ],
    "urgency_drivers": [
      "Operational decision state NEEDS_VERIFICATION due to evidence conflict/uncertainty"
    ]
  },
  "uncertainty": {
    "decision_state": "NEEDS_VERIFICATION",
    "confidence_level": "HIGH",
    "evidence_completeness": 0.85,
    "evidence_convergence": 0.75,
    "limiting_factors": [
      "Evidence contradiction detected in families: ['CONTEXT']"
    ]
  },
  "limitations": {
    "missing_context": false,
    "unavailable_evidence": [],
    "confidence_limitations": [
      "Evidence contradiction detected in families: ['CONTEXT']"
    ]
  }
}
```

---

## 9. Monotonicity & Safety Guarantees

1. **Hazard Monotonicity**: Increasing physical FRP or growth rate never reduces hazard score.
2. **Impact Monotonicity**: Adding industrial context or expanding footprint never reduces impact score.
3. **Priority Monotonicity**: Increasing urgency or verification requirement never reduces priority score.
4. **Safety Disclaimer**: The engine is an operational recommendation component. It does NOT make official emergency dispatch claims or replace human emergency command decisions.
