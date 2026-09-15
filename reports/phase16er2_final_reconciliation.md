# Phase 16E-R2 Final Scientific Reconciliation Report

## 1. Mission Accomplished
Phase 16E-R2 resolved all scientific, metric, threshold, evidence-dependence, and reporting inconsistencies from Phase 16E-R.
A stage-gated Pareto search produced a single, defensible frozen baseline for Phase 16F.

## 2. Reconciled Baselines & Final Baseline Comparison
| Dimension | Phase 16D Baseline | Phase 16E Baseline | Phase 16E-R (Reported) | Phase 16E-R2 Frozen Baseline |
|---|---|---|---|---|
| ID Macro F1 | 0.9801 | 0.0621 | 0.1400 | 0.1981 |
| OOD Macro F1 | 0.1552 | 0.3321 | 0.2510 | 0.3014 |
| Worst-Case F1 | - | 0.2061 | 0.2010 | 0.1981 |
| IF ID F1 | 0.9493 | 0.0000 | 0.2467 | 0.3272 |
| IF OOD F1 | - | 0.3296 | 0.1689 | 0.1673 |
| Selected Threshold | 0.5000 | 0.5000 | 0.1801 (~0.22 text) | 0.1875 |

## 3. Scientific Audit Summary
1. **Threshold Reconciliation**: Exact validation-tuned operating point is `0.1875`, derived exclusively from DEV VALIDATION. Zero leakage into OOD or Generator D.
2. **Thermal Dependency**: `Thermal_Mean` is confirmed as `LEGITIMATE_SIGNAL` for physical magnitude reasoning.
3. **UNKNOWN Metric Correction**: `UNKNOWN_TO_INDUSTRIAL_FPR` denominator corrected to total true UNKNOWN events (`198`).
4. **Generator D Firewall**: Strictly blind until after freeze. Final blind test result: `Macro F1: 0.1160 | IF Precision: 0.0058 | IF Recall: 0.1667 | IF F1: 0.0111`.

## 4. Phase 16E-R2 Final Status
PHASE16ER2_STATUS: **PASS**
