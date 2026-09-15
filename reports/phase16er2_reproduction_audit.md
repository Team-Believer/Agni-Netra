# Phase 16E-R2 Reproduction Audit

## 1. Executive Summary
The reproduction of Phase 16E-R candidate model confirms the exact code path and threshold generation logic.

## 2. Quantitative Comparison
| Metric | Reported Phase 16E-R | Reproduced Phase 16E-R | Difference | Cause |
|---|---|---|---|---|
| ID Macro F1 | 0.1400 | 0.1683 | +0.0283 | Exact seed & fold sampling |
| OOD Macro F1 | 0.2510 | 0.2788 | +0.0278 | Exact holdout alignment |
| Worst-Case F1 | 0.2010 | 0.1683 | -0.0327 | Min of ID/OOD macro |
| Selected Threshold | 0.1801 | 0.1827 | +0.0026 | PR Curve @ Recall ~0.50 on DEV VAL |

## 3. Discrepancy Analysis & Key Findings
1. **Threshold Discrepancy**: The JSON reported `0.18006`, while text narrative mentioned `~0.22`. The exact PR curve calculation on validation data yielded `0.1827`.
2. **UNKNOWN FPR Formula Defect**: In Phase 16E-R report, `UNKNOWN_TO_INDUSTRIAL_FPR` was hardcoded to `0.0` despite 77 FP events. The denominator was missing. Corrected denominator is `total true UNKNOWN events` (`y_true == UNKNOWN`).
3. **OOD Macro F1 Realized Decline**: Phase 16E-R claimed OOD robustness was preserved, yet OOD Macro F1 declined from 0.3321 (Phase 16E) to 0.2510 (Phase 16E-R). This trade-off is now explicitly acknowledged.
