# Phase 16E Experiment Manifest

## Baseline Freeze
- Phase 16D Macro F1 (ID): 0.9801
- Phase 16D Macro F1 (OOD Shifted): 0.1552
- Baseline Script: `freeze_16c.py` (which represents the neural representation state prior to the 16D audit).

## Datasets and Permissions
1. **In-Distribution (ID) Training**: `global_source_train.csv` - Permitted for Training Phase 16D baseline.
2. **Decorrelated Training**: `global_source_decorrelated.csv` - Permitted for Phase 16E Robust Training and Evidence Dropout tuning.
3. **OOD Generator Shift**: `global_source_shifted_holdout.csv` - Strict Evaluation Only. No tuning.
4. **Generator D (Adversarial)**: Protected. strictly BLIND_TEST_ONLY. No feature selection, hyperparameter tuning, or threshold adjustments are allowed.

## Evidence Taxonomy & Dropout Configuration
- **Thermal**: `meta_thermal_mean`, `meta_thermal_max`
- **History**: `meta_historical_recurrence` -> `history_missing` indicator
- **Context**: `meta_context_industry` -> `context_missing` indicator
- **Sentinel**: `meta_optical_sentinel` -> `sentinel_missing` indicator
- **Sensor**: `meta_sensor_agreement` -> `sensor_missing` indicator
