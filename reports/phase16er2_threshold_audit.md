# Phase 16E-R2 Threshold Audit

## 1. Selected Operating Threshold
SELECTED_THRESHOLD_EXACT: 0.1827
THRESHOLD_SOURCE_DATASET: DEVELOPMENT_VALIDATION (`global_source_decorrelated_val.csv`)
THRESHOLD_TUNING_USED_OOD: FALSE
THRESHOLD_TUNING_USED_GENERATOR_D: FALSE
THRESHOLD_LEAKAGE: NONE

## 2. Operating Point Evaluation (Frozen Threshold)
Evaluating frozen threshold `0.1827` without retuning:

| Split | IF Precision | IF Recall | IF F1 | Macro F1 |
|---|---|---|---|---|
| Development Validation | 0.1350 | 0.3503 | 0.1949 | - |
| ID Holdout | 0.1599 | 0.4192 | 0.2315 | 0.1683 |
| OOD Holdout | 0.0705 | 0.3889 | 0.1193 | 0.2788 |
