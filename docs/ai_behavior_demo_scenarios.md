# Phase 20H — Real-Data AI Behavioral Demonstration Scenarios

## Executive Overview

Phase 20H provides a deterministic, real-data demonstration suite (`src/intelligence/demo_scenarios.py`) illustrating how the consolidated **Agni-Netra** AI/ML intelligence engine (`analyze_event()`) differentiates behavioral scenarios on real FIRMS/VIIRS observations.

> [!IMPORTANT]
> **Core Operational Disclaimers:**
> - `REAL OBSERVATION != REAL GROUND TRUTH` (Detections represent observations, not verified gold-standard ground truth).
> - `SCENARIO LABEL != SOURCE CLASS` (Scenario titles describe observed system behavior and evidence patterns, not assumed physical source types).
> - `THESE ARE BEHAVIORAL DEMONSTRATIONS, NOT ACCURACY BENCHMARKS`.
> - If no real event in the corpus meets the fitness criteria for a scenario category, it is explicitly flagged as `AVAILABLE = FALSE` (`NO_REAL_EVENT_MEETS_SCENARIO_CRITERIA`). No scenarios are fabricated.

---

## 1. Scenario Definitions & Selection Criteria

The scenario suite evaluates 6 distinct behavioral categories against the real FIRMS/VIIRS reconstructed event corpus:

| Scenario ID | Scenario Name | Description & Fitness Scoring Criteria | Corpus Status | Selected Event |
| :--- | :--- | :--- | :---: | :--- |
| **SCENARIO 1** | Persistent / Routine Thermal Source | Repeated observations over time, sustained duration, stable low-T persistence signal (`LOW_T_PERSISTENT`). | **AVAILABLE** | `AGN-E-000871` |
| **SCENARIO 2** | Escalating / Abnormal Event | High observation count, thermal intensity changes, detected FRP change points, or elevated abnormality relative to baseline. | **AVAILABLE** | `AGN-E-000005` |
| **SCENARIO 3** | Sparse / Insufficient Observation | Singleton or sparse observations, triggering safe abstention (`INSUFFICIENT_OBSERVATION`) without fabricating history or persistence. | **AVAILABLE** | `AGN-E-000002` |
| **SCENARIO 4** | Conflicting Evidence Event | Disagreement between independent evidence families or contradictory sensor corroboration. | **UNAVAILABLE** (Explicit) | N/A (`AVAILABLE = FALSE`) |
| **SCENARIO 5** | Novel / OOD-like Event | Elevated novelty score, feature-space representation deviation, or model-confidence paradox (`distribution_state = NOVEL` / `UNKNOWN`). | **AVAILABLE** | `AGN-E-000003` |
| **SCENARIO 6** | High-Priority Event | Elevated physical hazard score, contextual facility impact, or operational urgency requiring verification. | **AVAILABLE** | `AGN-E-001105` |

---

## 2. Real Data Source & Provenance

- **Source Corpus**: Reconstructed real FIRMS/VIIRS event records from `data/interim/events/events.csv` and `data/interim/events/event_observations.csv`.
- **Inference Entrypoint**: `analyze_event()` under schema version `AGN-EVENT-INTELLIGENCE-1.0`.
- **Selection Rule**: Transparent, rule-based fitness scoring (`score_persistent_fitness`, `score_escalating_fitness`, `score_sparse_fitness`, etc.) with deterministic tie-breaking sorted by `(-fitness_score, event_id)`. Zero random sampling.
- **Traceability**: Each scenario record exposes `real_event_id`, `observation_ids`, spatial coordinates, time range, evidence family IDs, and machine-readable reason codes.

---

## 3. Scenario Comparison Matrix

The summary scenario matrix is exported to:
- [`docs/demo/ai_behavior_scenario_matrix.json`](file:///C:/Users/NIrmit/Desktop/Agni-Netra/Agni-Netra/docs/demo/ai_behavior_scenario_matrix.json)
- [`docs/demo/ai_behavior_scenario_matrix.md`](file:///C:/Users/NIrmit/Desktop/Agni-Netra/Agni-Netra/docs/demo/ai_behavior_scenario_matrix.md)

### Summary Table

| Scenario ID | Scenario Name | Event ID | Obs Count | Event State | Decision State | Distribution | Risk Level | Priority | Action | Available |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| SCENARIO_1 | PERSISTENT_ROUTINE_SOURCE | `AGN-E-000871` | 7 | `PERSISTING` | `UNKNOWN` | `KNOWN_LIKE` | `MODERATE` | `P3` | `INFORMATIONAL` | **TRUE** |
| SCENARIO_2 | ESCALATING_ABNORMAL_EVENT | `AGN-E-000005` | 37 | `STABLE` | `UNKNOWN` | `KNOWN_LIKE` | `LOW` | `P3` | `INFORMATIONAL` | **TRUE** |
| SCENARIO_3 | SPARSE_INSUFFICIENT_OBSERVATION | `AGN-E-000002` | 1 | `NEW` | `INSUFFICIENT_OBSERVATION` | `UNKNOWN` | `LOW` | `P3` | `INFORMATIONAL` | **TRUE** |
| SCENARIO_4 | CONFLICTING_EVIDENCE_EVENT | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | **FALSE** |
| SCENARIO_5 | NOVEL_OOD_LIKE_EVENT | `AGN-E-000003` | 1 | `NEW` | `INSUFFICIENT_OBSERVATION` | `UNKNOWN` | `LOW` | `P3` | `INFORMATIONAL` | **TRUE** |
| SCENARIO_6 | HIGH_PRIORITY_EVENT | `AGN-E-001105` | 5 | `PERSISTING` | `UNKNOWN` | `KNOWN_LIKE` | `MODERATE` | `P3` | `INFORMATIONAL` | **TRUE** |

---

## 4. Downstream Handoff Instructions

Backend, frontend, and presentation teams can access the demonstration package programmatically via Python or JSON:

### Python Access
```python
from src.intelligence.demo_scenarios import select_demo_scenarios, build_and_export_demo_package

# Retrieve selected demo scenario package
scenarios = select_demo_scenarios()
for scenario_id, sc in scenarios.items():
    if sc.available:
        print(f"{sc.scenario_id}: Event {sc.real_event_id} -> State: {sc.ai_result['event_state']}, Priority: {sc.ai_result['priority_level']}")
    else:
        print(f"{sc.scenario_id}: UNAVAILABLE ({sc.unavailable_reason})")
```

### JSON Access
Read [`docs/demo/ai_behavior_scenario_matrix.json`](file:///C:/Users/NIrmit/Desktop/Agni-Netra/Agni-Netra/docs/demo/ai_behavior_scenario_matrix.json) directly.
