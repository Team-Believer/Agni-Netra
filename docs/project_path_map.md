# Agni-Netra Project File & Path Map

> [!IMPORTANT]
> **Authoritative Path Map & Discovery Directory**
> - **Schema Version**: `AGN-EVENT-INTELLIGENCE-1.0`
> - **Final Frozen Model Asset**: `models/b0/xgboost_b0.json` (SHA-256: `b867eb14a14d23507294cb1402ad0530aa94f998b4e74414da6105a77d24ba21`)
> - **Ground-Truth Disclaimer**: `REAL OBSERVATION != REAL GROUND TRUTH`. Real-world ground truth gold standard (`REAL_GOLD`) is **NOT ESTABLISHED**.

---

## 1. Searchable Quick Reference

| Asset / Functionality | Relative Path | Status |
| :--- | :--- | :---: |
| **Final Frozen Model** | `models/b0/xgboost_b0.json` | `[FROZEN]` |
| **Model Inference Code** | `src/model/inference_b0.py` | `[CURRENT]` |
| **Main AI Entrypoint** | `src/intelligence/analyze_event.py` | `[CURRENT]` |
| **AI Output Contract** | `src/intelligence/output_contract.py` | `[FROZEN]` |
| **AI Output Schema Doc** | `docs/ai_output_contract.md` | `[DOC]` |
| **Observation Quality Layer** | `src/intelligence/observation_quality.py` | `[CURRENT]` |
| **Low-T Persistent Heat** | `src/features/low_t_persistent_heat.py` | `[CURRENT]` |
| **High-T Thermal Physics** | `src/intelligence/high_t_thermal.py` | `[CURRENT]` |
| **Event State Machine** | `src/intelligence/event_state_machine.py` | `[CURRENT]` |
| **INSAT-3DS Ingestion** | `src/ingestion/insat3ds.py` | `[CURRENT]` |
| **Novel / OOD Detection** | `src/intelligence/novel_event_detection.py` | `[CURRENT]` |
| **Evidence Ledger & Fusion** | `src/intelligence/evidence_aggregation.py` | `[CURRENT]` |
| **Confidence & UNKNOWN Engine**| `src/intelligence/confidence_decision.py` | `[CURRENT]` |
| **Risk & Priority Engine** | `src/intelligence/risk_priority.py` | `[CURRENT]` |
| **Explanation Engine** | `src/intelligence/explanation_engine.py` | `[CURRENT]` |
| **Real FIRMS Normalized Data** | `data/interim/firms_normalized.csv` | `[DATA]` |
| **Reconstructed Events Data** | `data/interim/events/events.csv` | `[DATA]` |
| **Real-Data Replay Harness** | `src/intelligence/real_event_replay.py` | `[CURRENT]` |
| **Demo Scenarios Selector** | `src/intelligence/demo_scenarios.py` | `[DEMO]` |
| **Demo Scenario Matrix** | `docs/demo/ai_behavior_scenario_matrix.md` | `[DEMO]` |

---

## 2. "Where Do I Find..." FAQ Navigation Table

| What I Need | Relative Path | Notes |
| :--- | :--- | :--- |
| **Final Frozen Model Checkpoint** | `models/b0/xgboost_b0.json` | Frozen XGBoost model asset |
| **Model Config & Features** | `models/b0/model_config.json` | Model feature list & parameters |
| **Model Label Mapping** | `models/b0/label_mapping.json` | Numeric label to class mapping |
| **Model Inference Code** | `src/model/inference_b0.py` | Inference loader & execution class |
| **Model Training Code** | `src/model/train_b0.py` | Training script (Frozen Phase 16E-R2) |
| **Canonical Feature Extraction** | `src/features/canonical_event_features.py` | 35+ online-safe features |
| **Observation Quality Defense** | `src/intelligence/observation_quality.py` | Saturation & daytime glint defense |
| **Low-T Persistent Heat Lane** | `src/features/low_t_persistent_heat.py` | Low-T persistence intelligence |
| **High-T Thermal Physics Lane** | `src/intelligence/high_t_thermal.py` | High-T thermal intensity & T4/T11 |
| **INSAT-3DS Ingestion Engine** | `src/ingestion/insat3ds.py` | GEO high-cadence evidence lane |
| **Event Reconstruction Code** | `src/data/event_reconstruction.py` | DBSCAN spatiotemporal clustering |
| **Event State Machine** | `src/intelligence/event_state_machine.py` | 10 behavioral state transitions |
| **Historical Abnormality Engine** | `src/intelligence/historical_abnormality.py` | Baseline abnormality & change points |
| **Novel / OOD Engine** | `src/intelligence/novel_event_detection.py` | 6 OOD signals & model-confidence paradox |
| **Evidence Ledger & Fusion** | `src/intelligence/evidence_aggregation.py` | Provenance-aware evidence fusion |
| **Confidence & UNKNOWN Engine** | `src/intelligence/confidence_decision.py` | Calibrated confidence & safe abstention |
| **Risk & Priority Engine** | `src/intelligence/risk_priority.py` | Base risk, urgency, priority `P0`–`P4` |
| **Explanation Engine** | `src/intelligence/explanation_engine.py` | WHY / WHY NOT / WHAT CHANGED |
| **Unified Entry Point** | `src/intelligence/analyze_event.py` | Orchestrates 13 intelligence stages |
| **Output Contract & Validator** | `src/intelligence/output_contract.py` | Contract builder & schema validator |
| **Handoff Output JSON Example** | `docs/examples/event_intelligence_example.json` | Sample 16-section handoff output |
| **Real-Data Replay Harness** | `src/intelligence/real_event_replay.py` | AI-side real FIRMS event replay |
| **Demo Scenario Selector** | `src/intelligence/demo_scenarios.py` | Extracts 6 behavioral scenarios |
| **Demo Scenario Matrix** | `docs/demo/ai_behavior_scenario_matrix.md` | Markdown scenario matrix table |
| **Normalized Real FIRMS Data** | `data/interim/firms_normalized.csv` | Normalized VIIRS satellite detections |
| **Reconstructed Real Events** | `data/interim/events/events.csv` | Reconstructed real event table |
| **Configuration Files** | `configs/` | Anomaly, reconstruction, Sentinel configs |
| **Pytest Unit/Integration Tests** | `tests/` | 19 test modules (256 test cases) |
| **Master Architecture Document** | `docs/ai_ml_final_architecture.md` | Single source of truth architecture doc |

---

## 3. Frozen Final Model & Asset Classification

### Primary Production Model Asset (`FROZEN_PRODUCTION_MVP`)
- **Relative Path**: `models/b0/xgboost_b0.json`
- **Absolute Path**: `C:\Users\NIrmit\Desktop\Agni-Netra\Agni-Netra\models\b0\xgboost_b0.json`
- **Model Type**: Multi-class Gradient Boosted Decision Trees (XGBoost)
- **Model Format**: Native JSON serialization (`xgboost.Booster`)
- **SHA-256 Hash**: `b867eb14a14d23507294cb1402ad0530aa94f998b4e74414da6105a77d24ba21`
- **Inference Code Path**: `src/model/inference_b0.py`
- **Configuration Path**: `models/b0/model_config.json`
- **Label Mapping Path**: `models/b0/label_mapping.json`
- **Status**: `[FROZEN]` (Phase 16E-R2)

---

## 4. AI/ML Source Tree (`src/`)

```
src/
├── intelligence/
│   ├── analyze_event.py          [CURRENT] Unified 13-stage entry point
│   ├── output_contract.py        [FROZEN]  Contract builder & schema validator
│   ├── observation_quality.py    [CURRENT] Saturation & daytime glint defense
│   ├── event_state_machine.py    [CURRENT] 10 behavioral state transitions
│   ├── high_t_thermal.py         [CURRENT] High-T thermal intensity & T4/T11
│   ├── historical_abnormality.py [CURRENT] Baseline abnormality & change points
│   ├── novel_event_detection.py  [CURRENT] Multi-signal OOD & confidence paradox
│   ├── evidence_aggregation.py   [CURRENT] Provenance-aware evidence ledger
│   ├── confidence_decision.py    [CURRENT] Calibrated confidence & abstention
│   ├── risk_priority.py          [CURRENT] Risk, urgency & priority P0-P4
│   ├── explanation_engine.py     [CURRENT] WHY / WHY NOT / WHAT CHANGED
│   ├── real_event_replay.py      [CURRENT] Real-data replay harness
│   └── demo_scenarios.py         [DEMO]    Behavioral scenario selector
├── features/
│   ├── canonical_event_features.py [CURRENT] 35+ online-safe features
│   ├── low_t_persistent_heat.py    [CURRENT] Low-T persistence intelligence
│   ├── anomaly_engine.py           [CURRENT] Feature-level anomaly scoring
│   ├── historical_fingerprint.py  [CURRENT] Historical baseline profiling
│   ├── sentinel2_corroboration.py  [CURRENT] Sentinel-2 corroboration hook
│   └── sentinel2_raster_corroboration.py [CURRENT] Raster corroboration hook
├── ingestion/
│   └── insat3ds.py                [CURRENT] GEO high-cadence thermal evidence
└── model/
    ├── inference_b0.py            [CURRENT] XGBoost inference wrapper
    └── train_b0.py                [LEGACY]  Phase 16E-R2 model training
```

---

## 5. 13-Stage AI Inference Pipeline Map

All event inference flows through `analyze_event()` in `src/intelligence/analyze_event.py`:

| Stage | Name | Responsible File | Key Function / Class |
| :---: | :--- | :--- | :--- |
| **1** | Input Validation | `src/intelligence/analyze_event.py` | `_validate_event_input()` |
| **2** | Observation Quality | `src/intelligence/observation_quality.py` | `evaluate_event_observation_quality()` |
| **3** | Canonical Features | `src/features/canonical_event_features.py` | `build_event_features()` |
| **4** | Low-T Persistent Heat | `src/features/low_t_persistent_heat.py` | `evaluate_low_t_lane()` |
| **5** | High-T Thermal Physics | `src/intelligence/high_t_thermal.py` | `evaluate_high_t_lane()` |
| **6** | Event State Machine | `src/intelligence/event_state_machine.py` | `evaluate_event_state_machine()` |
| **7** | Historical Abnormality | `src/intelligence/historical_abnormality.py` | `evaluate_abnormality()` |
| **8** | Multitask Model Inference| `src/model/inference_b0.py` | `AgniNetraB0Inference.predict_event()` |
| **9** | Novel / OOD Detection | `src/intelligence/novel_event_detection.py` | `evaluate_event_novelty()` |
| **10** | Evidence Fusion | `src/intelligence/evidence_aggregation.py` | `aggregate_event_evidence()` |
| **11** | Confidence & Abstention | `src/intelligence/confidence_decision.py` | `evaluate_event_decision()` |
| **12** | Risk & Operational Priority| `src/intelligence/risk_priority.py` | `evaluate_risk_and_priority()` |
| **13** | Explanation Engine | `src/intelligence/explanation_engine.py` | `generate_explanation()` |

---

## 6. Data Directory Path Map (`data/`)

```
data/
├── interim/
│   ├── firms_normalized.csv            [DATA] Normalized real VIIRS detection records
│   ├── firms_historical_real_normalized.csv [DATA] Multi-year historical VIIRS records
│   └── events/
│       ├── events.csv                  [DATA] 3,304 reconstructed real events
│       └── event_observations.csv      [DATA] Observation-to-event association table
├── raw/
│   ├── external_evidence.csv           [DATA] External context evidence
│   ├── firms/
│   │   ├── noaa_20_viirs_south_asia_7d.csv [DATA] Raw NOAA-20 VIIRS 7-day CSV
│   │   └── suomi_npp_viirs_south_asia_7d.csv [DATA] Raw Suomi-NPP VIIRS 7-day CSV
│   └── osm/                            [DATA] OpenStreetMap facility context data
├── ground_truth/                       [DATA] Reference manifests (REAL_GOLD = NOT ESTABLISHED)
└── synthetic/                          [DATA] Synthetic reference datasets (Explicitly synthetic)
```

---

## 7. Configuration Directory Map (`configs/`)

- `configs/event_reconstruction.yaml` — DBSCAN spatial radius (1.5 km), gap hours (24h), min samples.
- `configs/event_reconstruction_90d.yaml` — Long-window 90-day event clustering settings.
- `configs/anomaly_engine.yaml` — Historical baseline deviation thresholds.
- `configs/historical_fingerprint.yaml` — Facility thermal recurrence profiling parameters.
- `configs/sentinel2.yaml` — Sentinel-2 band wavelengths and index thresholds.

---

## 8. Test Directory Map (`tests/`)

All 19 test modules reside in `tests/` and validate end-to-end correctness (`256 passed in 4.54s`):

- `tests/test_analyze_event.py` — Verifies 13-stage pipeline execution, order, and determinism.
- `tests/test_canonical_event_features.py` — Verifies feature extraction and online safety.
- `tests/test_confidence_decision.py` — Verifies confidence calibration and safe abstention gating.
- `tests/test_demo_scenarios.py` — Verifies deterministic behavioral scenario selection.
- `tests/test_event_state_machine.py` — Verifies state transitions across all 10 states.
- `tests/test_evidence_aggregation.py` — Verifies evidence fusion and ledger completeness.
- `tests/test_explanation_engine.py` — Verifies WHY, WHY_NOT, WHAT_CHANGED outputs.
- `tests/test_feature_engine.py` — Verifies feature generator utilities.
- `tests/test_high_t_thermal.py` — Verifies high-T physics and T4/T11 thermal intensity.
- `tests/test_historical_abnormality.py` — Verifies baseline abnormality and FRP change points.
- `tests/test_insat3ds_ingestion.py` — Verifies INSAT-3DS GEO thermal evidence lane.
- `tests/test_low_t_pipeline.py` — Verifies low-T persistent heat evaluation.
- `tests/test_multitask_model.py` — Verifies model inference wrapper.
- `tests/test_novel_event_detection.py` — Verifies 6 OOD signals and model-confidence paradox.
- `tests/test_observation_quality.py` — Verifies saturation and daytime solar glint defense.
- `tests/test_output_contract.py` — Verifies contract builder and schema validator.
- `tests/test_real_event_replay.py` — Verifies real-data replay harness and consistency auditor.
- `tests/test_risk_priority.py` — Verifies base risk, urgency, and priority levels `P0`–`P4`.
- `tests/test_temporal_model.py` — Verifies temporal feature calculations.

---

## 9. Documentation Directory Map (`docs/`)

- `docs/ai_ml_final_architecture.md` — `[DOC]` Master Architecture Document (Source of Truth).
- `docs/ai_output_contract.md` — `[DOC]` Schema Contract Specification (`AGN-EVENT-INTELLIGENCE-1.0`).
- `docs/real_data_ai_readiness.md` — `[DOC]` Real-Data Replay & Pipeline Readiness Report.
- `docs/ai_behavior_demo_scenarios.md` — `[DOC]` Behavioral Demonstration Scenarios Report.
- `docs/observation_quality_layer.md` — `[DOC]` Saturation & Solar Glint Defense Documentation.
- `docs/insat3ds_integration.md` — `[DOC]` INSAT-3DS High-Cadence GEO Evidence Documentation.
- `docs/high_t_thermal_physics.md` — `[DOC]` High-T Thermal Physics Lane Documentation.
- `docs/event_state_machine.md` — `[DOC]` Event State Machine Specification.
- `docs/novel_ood_event_intelligence.md` — `[DOC]` Novelty & OOD Intelligence Documentation.
- `docs/confidence_calibration_and_unknown.md` — `[DOC]` Confidence & UNKNOWN Engine Documentation.
- `docs/risk_priority_engine.md` — `[DOC]` Risk & Priority Intelligence Documentation.
- `docs/explanation_engine.md` — `[DOC]` Explanation Engine Specification.
- `docs/unified_analyze_event_pipeline.md` — `[DOC]` Unified Pipeline Orchestration Specification.
- `docs/examples/event_intelligence_example.json` — `[EXAMPLES]` Sample 16-Section Output JSON.
- `docs/demo/ai_behavior_scenario_matrix.md` — `[DEMO]` Scenario Comparison Matrix Table.
- `docs/demo/ai_behavior_scenario_matrix.json` — `[DEMO]` Scenario Package JSON Output.

---

## 10. AI Handoff Contract Summary

Downstream backend, REST API, database, and frontend teams must consume the single AI entry point and frozen output contract:

- **AI Entry Point**: `analyze_event()` in `src/intelligence/analyze_event.py`
- **Output Schema**: `AGN-EVENT-INTELLIGENCE-1.0` enforced by `src/intelligence/output_contract.py`
- **Validation**: `validate_event_intelligence_result(result)`
- **Sample Output Payload**: `docs/examples/event_intelligence_example.json`

---

## 11. Path Validation Report

Programmatic path validation results for all documented paths in this project:

- **TOTAL_PATHS_DOCUMENTED**: 52
- **VALID_PATHS**: 52
- **INVALID_PATHS**: 0
- **UNVERIFIED_PATHS**: 0
