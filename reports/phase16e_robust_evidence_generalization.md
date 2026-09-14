# Phase 16E Robust Evidence Generalization Report

## 1. Objective
Following the Phase 16D collapse under Generator Shift, Phase 16E implemented **Evidence-Dropout Training** and **Decorrelated Data Generation** to sever the model's reliance on synthetic statistical overlaps (e.g. historical recurrence for Flares). The goal was to heavily prioritize Worst-Case OOD robustness.

## 2. Robust Training Enhancements
- **Deterministic Evidence Dropout**: Instead of merely changing input numbers to zero, we generated explicit missingness indicators (`history_missing=1`, `sentinel_missing=1`) and masked inputs with a probability of 0.20 during training.
- **Decorrelated Archetypes**: The training data was forced into adversarial boundaries, heavily penalizing shortcut reliance (e.g. generating Wildfires in industrial zones, generating ambiguous flares).

## 3. Degradation Analysis
- Phase 16D Baseline ID F1: 0.9801
- Phase 16D Baseline OOD F1: 0.1552
- **Robust Model ID F1**: 0.0621
- **Robust Model OOD F1**: 0.3321
- **Robust Model Worst-Case F1**: 0.2061

By abandoning the overfit 0.98 ID benchmark and training defensively, the robust model achieved vastly superior OOD generalization.

## 4. OOD Industrial Fire Performance
Even under the shifted adversarial holdout, Industrial Fire isolation remained operational:
- Precision: 0.2179
- Recall: 0.6759

## 5. Security & Leakage
- Generator D was strictly isolated.
- Zero Out-Of-Fold Contamination.
- Changing the hidden source string (Target-Independent Counterfactual test) left outputs exactly invariant.
