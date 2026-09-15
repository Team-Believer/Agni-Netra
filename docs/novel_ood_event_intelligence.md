# Agni-Netra Phase 20E: Novel / Out-of-Distribution (OOD) Event Intelligence

## 1. Core Principles & Mandates

```
OOD != CLASSIFICATION
NOVEL != UNKNOWN
UNKNOWN != NO EVENT
ABNORMALITY != NOVELTY
HIGH MODEL CONFIDENCE != KNOWN DISTRIBUTION
DATA QUALITY FAILURE != NOVEL EVENT
```

Real industrial environments contain novel, uncatalogued, or poorly represented thermal phenomena (e.g., unusual chemical reactors, battery thermal events, metal-processing heat, or mixed-source events). Agni-Netra prevents forced classification of novel events by maintaining a dedicated Novelty / OOD Intelligence layer.

---

## 2. Decoupled Distribution States & Levels

| Distribution State | Description | Decision Path |
| :--- | :--- | :--- |
| `KNOWN_LIKE` | Event pattern is consistent with known training archetypes | Normal classification decision path |
| `NOVEL` | Multi-signal evidence indicates event is out-of-distribution | Triggers `NEEDS_VERIFICATION` or `UNKNOWN` (forces safe abstention) |
| `UNKNOWN` | Data quality or observation count is insufficient to assess novelty | Triggers `INSUFFICIENT_OBSERVATION` / `UNKNOWN` |

Novelty Levels: `KNOWN_LIKE`, `LOW_NOVELTY`, `MODERATE_NOVELTY`, `HIGH_NOVELTY`, `NOVEL`, `UNKNOWN`.

---

## 3. Component OOD Signals

The novelty score is derived from six component signals:

1. **Feature-Space Distance**: Normalized distance from known reference feature distributions.
2. **Class-Space Uncertainty**: Classifier margin and entropy ambiguity.
3. **Evidence Disagreement**: Contradictions across independent evidence families.
4. **Temporal Novelty**: Temporal transition morphology relative to known source behaviors.
5. **Context Novelty**: Unprecedented thermal intensity in non-industrial or rural context archetypes.
6. **Behavioral Novelty**: Unusual combinations of High-T intensity and Low-T persistence.

---

## 4. Key Disambiguation Rules

### A. High-Confidence OOD Paradox
A classifier may output high raw confidence ($\ge 0.75$) for a known class while the OOD engine measures high feature/behavioral distance ($\ge 0.60$).
- **Handling**: Flagged as `HIGH_CONFIDENCE_OOD`. Automatically forces `distribution_state = NOVEL` and `decision_recommendation = NEEDS_VERIFICATION`.

### B. OOD vs. Data Quality & Temporal Sparsity
Degraded observation quality or sparse temporal history (e.g. single observation) does **not** equal `NOVEL`.
- **Handling**: Categorized as `LOW_DATA_QUALITY_FOR_OOD` or `INSUFFICIENT_DATA_FOR_OOD` with `distribution_state = UNKNOWN`.

### C. OOD vs. Evidence Conflict
Contradictory evidence across sensor families is tagged as `EVIDENCE_CONFLICT_NOT_NOVEL`, triggering `NEEDS_VERIFICATION` rather than `NOVEL`.

### D. Abnormality vs. Novelty
Local historical baseline deviation (Phase 17C Abnormality) is kept separate from archetype novelty (Phase 20E OOD). A source can be `ABNORMAL` without being `NOVEL`.

---

## 5. System & Downstream Integrations

1. **Evidence Ledger (Phase 17D)**: Emits evidence items under family `OOD_NOVELTY` (`SUPPORTING`, `NEUTRAL`, `MISSING`).
2. **Confidence Engine (Phase 17E)**: `distribution_state == "NOVEL"` prevents autonomous `KNOWN` decision, forcing `NEEDS_VERIFICATION` or `UNKNOWN`.
3. **Risk & Operational Priority (Phase 17F)**: Novelty affects verification priority and investigation urgency without artificially forcing high physical hazard.
4. **Explanation Engine (Phase 17G)**: Produces controlled phrasing (*"Event shows high novelty relative to known source patterns; classification requires verification"*, never *"AI discovered a new type of fire"*).
5. **Orchestrator (`analyze_event()`)**: Executes as Stage 8: `novel_event_detection` right after model inference. Output is exposed under `source_assessment`.
