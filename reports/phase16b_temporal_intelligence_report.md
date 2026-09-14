# Phase 16B Temporal Intelligence Integrity Audit

## 1. Objective
Physically construct distinct ablation variants, verify strict target isolation, and evaluate `ALL_EVENT` vs `COVERED_SET` metrics to rigorously quantify incremental auxiliary evidence utility without artificially chasing F1.

## 2. Real Data Limitation
REAL_GOLD = 0.
- **REAL FIRMS DATA**: Used solely for temporal structure (sequence distribution auditing).
- **CONTROLLED SYNTHETIC DATA**: Used for temporal sequence learning.
- **GENERATOR D**: Used purely for adversarial stress testing. No real-world accuracy claims are inferred.

## 3. Ablation Input Schema Audit
| Model | Feature Count | Schema Hash | Tensor Shape | Missing Rates |
|---|---|---|---|---|
| GRU_ONLY | 2 | `6d7a3a93` | [1, 2] | Valid |
| GRU_HISTORY | 3 | `9aad8249` | [1, 3] | Valid |
| GRU_ANOMALY | 3 | `35f1ce3f` | [1, 3] | Valid |
| GRU_CONTEXT | 4 | `d81dc641` | [1, 4] | Valid |
| FULL_HYBRID | 6 | `122562af` | [1, 6] | Valid |

*Conclusion*: All 5 ablations are physically distinct architectures consuming different input schemas. There is no input contamination. S2_NDVI_online is represented correctly as available evidence or explicit missingness (NaN).

## 4. Feature-Destruction Sanity Test
Proving that the `FULL_HYBRID` model actively consumed the auxiliary tensors:
- **HISTORY_DESTROYED**: Metric Difference Detected? True (Predictions changed: 24)
- **ANOMALY_DESTROYED**: Metric Difference Detected? True (Predictions changed: 133)
- **CONTEXT_DESTROYED**: Metric Difference Detected? True (Predictions changed: 474)

## 5. Metric Denominator Separation & Model Ranking
The following evaluation uses the identical frozen independent holdout. 
- **ALL_EVENT_MACRO_F1**: Computed across ALL holdout events. Abstentions (conf < 0.60) are rigorously routed to UNKNOWN and heavily penalized.
- **COVERED_SET_MACRO_F1**: Computed ONLY on events where the model did not abstain (Selective Performance).

| Model | ALL_EVENT Macro F1 | COVERED_SET Macro F1 | ALL_EVENT Ind F1 | COVERED_SET Ind F1 | Coverage | Abstention Rate |
|---|---|---|---|---|---|---|
| STATIC (Base) | 0.7612 | 0.7612 | 0.7050 | 0.7050 | 100.0% | 0.0% |
| TEMP_AGGREGATE | 0.7887 | 0.7887 | 0.7850 | 0.7850 | 100.0% | 0.0% |
| GRU_ONLY | 0.2526 | 0.9307 | 0.4045 | 0.9000 | 35.90% | 64.10% |
| GRU_HISTORY | 0.2305 | 0.9647 | 0.2922 | 0.9431 | 31.70% | 68.30% |
| GRU_ANOMALY | 0.2340 | 0.6346 | 0.3020 | 0.9173 | 32.80% | 67.20% |
| GRU_CONTEXT | 0.4178 | 0.6968 | 0.7225 | 0.8907 | 62.10% | 37.90% |
| FULL_HYBRID | 0.5050 | 0.7231 | 0.6353 | 0.9235 | 64.30% | 35.70% |

*Conclusion*: XGBoost temporal aggregates remain the stronger ALL_EVENT baseline under this evaluation. The GRU is a TEMPORAL REPRESENTATION / SEQUENCE MODEL CANDIDATE, not a superior final classifier. While GRU covered-set F1 is high, coverage is limited, and all-event performance is lower than the temporal aggregate baseline.

Furthermore, contextual signals materially affect selective coverage in this synthetic experiment (GRU_ONLY coverage=35.9% vs GRU_CONTEXT coverage=62.1%). This is CONTROLLED SYNTHETIC EVIDENCE and does not prove real-world Sentinel/OSM benefit.

## 6. Early Detection (Prefix Metrics)
| Prefix | Total Events | Covered Events | Coverage | ALL_EVENT Macro F1 | COVERED_SET Macro F1 |
|---|---|---|---|---|---|
| T1 | 1000 | 533 | 53.30% | 0.4429 | 0.6983 |
| T2 | 1000 | 637 | 63.70% | 0.4975 | 0.7159 |
| T3 | 1000 | 637 | 63.70% | 0.5004 | 0.7196 |
| T4 | 1000 | 638 | 63.80% | 0.5011 | 0.7202 |
| T5 | 1000 | 638 | 63.80% | 0.5011 | 0.7202 |

## 7. Generator D Safety
- **total_D_events**: 1000
- **abstained_events**: 240
- **retained_events**: 760
- **abstention_rate**: 24.00% (The model abstained on 24.00% of adversarial cases)
- **high_confidence_predictions**: 760
- **high_confidence_false_positives**: 184
- **high_confidence_FPR**: 0.2421

*Conclusion*: Generator D exposes a substantial adversarial false-positive failure mode despite partial abstention. This failure motivates stronger unknown rejection and evidence-fusion logic in later phases.

## 8. Sensor Drop (ALL_EVENT Macro F1)
- **ALL SENSORS**: 0.5050
- **NO_N20**: 0.4876
- **NO_N21**: 0.4811
- **NO_NPP**: 0.4762

## 9. Structural Integrity & Reproducibility
- **Event Split Firewall**: PASS (Intersection of train/val/test event sets programmatically verified empty).
- **Target Firewall**: PASS (`TRUE_SYNTHETIC_CLASS` explicitly blocked from feature ingest).
- **Independent Holdout Protection**: PASS (Generated via Seed 9999 prior to tuning, untouched by hyperparameter selection or early stopping).
- **Reproducibility**: PASS (Tolerance delta < 0.001 across identical independent seeds).

## 10. Final Scientific Conclusion
Phase 16B establishes a causal temporal modeling pipeline. In the controlled synthetic evaluation, the temporal aggregate baseline remained stronger on all-event Macro F1, while GRU models achieved higher selective performance at reduced coverage. Context-bearing variants substantially increased coverage relative to GRU-only inference. Generator D revealed a meaningful high-confidence false-positive failure mode. These findings motivate the next phase: multi-task source/behavior/unknown modeling and stronger evidence fusion.
