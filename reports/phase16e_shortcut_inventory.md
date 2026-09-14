# Phase 16E Shortcut Inventory

| feature | feature_type | single_feature_predictability (MI) | depends_on_source_target | shortcut_risk | decision |
|---------|-------------|------------------------------------|---------------------------|---------------|----------|
| `meta_thermal_mean` | Direct | 0.72 | YES (indirectly through generator overlapping rules) | SYNTHETIC_SHORTCUT_RISK | AMBIGUOUS_REMOVE_PENDING_REVIEW (Must be decorrelated) |
| `meta_thermal_max` | Direct | 0.71 | YES (indirectly) | SYNTHETIC_SHORTCUT_RISK | AMBIGUOUS_REMOVE_PENDING_REVIEW (Must be decorrelated) |
| `meta_temporal_len` | Direct | 0.32 | NO (weak correlation) | LEGITIMATE_OVERLAP | TARGET_INDEPENDENT |
| `meta_historical_recurrence` | Direct | 0.94 | YES (Flares heavily biased) | SYNTHETIC_SHORTCUT_RISK | TARGET_DEPENDENT (Remove deterministic linkage) |
| `meta_context_industry` | Direct | 0.68 | YES (Industrial bias) | SYNTHETIC_SHORTCUT_RISK | TARGET_DEPENDENT (Remove deterministic linkage) |
| `meta_optical_sentinel` | Direct | 0.10 | NO | LEGITIMATE_OVERLAP | TARGET_INDEPENDENT |
| `meta_sensor_agreement` | Direct | 0.31 | NO | LEGITIMATE_OVERLAP | TARGET_INDEPENDENT |

**Conclusion**: The underlying generation rules strongly linked `meta_historical_recurrence` to Routine Flares and `meta_context_industry` to Industrial Fires. We must build a Decorrelated Generator that probabilistically overlaps these ranges so that single features cannot trivially predict the Target.
