# Phase 16D Scientific Validity Audit Report

## 1. Target-Predictability & Lineage Audit
- `meta_thermal_mean` (MI: 0.72) -> SYNTHETIC_SHORTCUT_RISK
- `meta_historical_recurrence` (MI: 0.94) -> SYNTHETIC_SHORTCUT_RISK
- `meta_context_industry` (MI: 0.69) -> SYNTHETIC_SHORTCUT_RISK
- **Conclusion**: No raw target strings leaked, but the synthetic generation priors made classes easily separable via contextual/historical thresholds.

## 2. Generator-Shift Test
- **Shifted OOD Holdout Macro F1**: 0.1552
- The model F1 collapsed from 0.98 down to ~0.15 when the underlying synthetic correlations (e.g., flares having high recurrence) were broken. This proves the high performance was a **GENERATOR ARTIFACT**, not absolute truth.

## 3. OOF Stacking Firewall
- TRAIN INTERSECT OOF = 0
- TRAIN INTERSECT HOLDOUT = 0
- META_TRAIN INTERSECT HOLDOUT = 0

## 4. Perfect-Class Explanation
Routine Flare achieved F1=1.0 because the generator heavily anchored it to historical recurrence. Under OOD shift, its F1 collapsed to 0.0000, proving the perfect score was a synthetic artifact rather than an information leak.
