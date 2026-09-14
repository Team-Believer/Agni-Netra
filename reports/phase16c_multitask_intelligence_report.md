# Phase 16C Decision Policy / Coverage Remediation Report

## 1. Objective
Redesign the Evidence-Fusion hierarchy to minimize `UNNECESSARY_UNKNOWN` and improve coverage, without sacrificing the safety ceiling (i.e. preventing confident false alarms on Industrial Fire).

## 2. Definitions
- **UNNECESSARY_UNKNOWN**: True label is known, raw model argmax correctly predicts it, but policy rejects it.
- **JUSTIFIED_UNKNOWN**: True ambiguity, conflict, insufficient evidence, or OOD pattern.

## 3. Abstention Reason Breakdown (Best Point)
- EVIDENCE_INSUFFICIENT: 1
- UNKNOWN_GATE: 63
- LOW_SOURCE_MARGIN: 3
- HIGH_CONFLICT: 1
- LOW_MODEL_CONFIDENCE: 1056

## 4. Industrial Fire Confusion Matrix
| Metric | Value |
|---|---|
| True Positive | 29 |
| False Positive | 13 |
| False Negative | 260 |
| True Negative | 1698 |
| Precision | 0.6905 |
| Recall | 0.1003 |
| F1 | 0.1752 |

## 5. Threshold Grid & 6. Pareto Frontier
Operating points balancing Confidence Threshold against Unknown Threshold.
Max achieved coverage is 43.75% at Conf=0.5, Unk=0.5. The bottleneck is currently raw model confidence.

## 7. Hard Negative Sensitivity
| Ratio | Target F1 | Coverage |
|---|---|---|
| 10% | 0.2099 | 29.10% |
| 15% | 0.0273 | 24.65% |
| 20% | 0.0977 | 27.70% |

## 8. Selected Operating Point
**Unknown Threshold**: 0.5
**Confidence Threshold**: 0.5
- **UNKNOWN_RATE**: 56.25%
- **UNNECESSARY_UNKNOWN_RATE**: 18.15%
- **JUSTIFIED_UNKNOWN_RATE**: 38.10%

## 9. Generator D Stress Results
- **Abstention Rate**: 87.20%
- **High_Conf_FP**: 2

## 10. Integrity Results
- **Target Firewall**: PASS
- **Holdout Integrity**: PASS
