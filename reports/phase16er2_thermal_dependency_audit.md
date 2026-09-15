# Phase 16E-R2 Thermal Dependency Audit

## 1. Executive Summary
Evaluation of thermal feature ablations demonstrates that `Thermal_Mean` serves as `LEGITIMATE_SIGNAL`.
It provides necessary physical magnitude signal (distinguishing high-energy flares/industrial heat from ambient ground) without acting as a single deterministic 1:1 synthetic shortcut.

## 2. Feature Ablation Matrix (OOD Holdout)
| Ablation Setup | Macro F1 | IF Precision | IF Recall | IF F1 |
|---|---|---|---|---|
| Full Model | 0.3014 | 0.0974 | 0.5926 | 0.1673 |
| Remove Thermal Mean | 0.2911 | 0.1138 | 0.2593 | 0.1582 |
| Remove All Thermal | 0.2911 | 0.1138 | 0.2593 | 0.1582 |
| Thermal Only | 0.1011 | 0.0551 | 0.5370 | 0.0999 |
| Non-Thermal Only | 0.2911 | 0.1138 | 0.2593 | 0.1582 |

PRIMARY_EVIDENCE_DEPENDENCY = Thermal_Mean (Legitimate Physical Evidence)
THERMAL_MEAN_DEPENDENCY_CLASSIFICATION = LEGITIMATE_SIGNAL
NEW_SYNTHETIC_SHORTCUT = None detected
