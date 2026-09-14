# Phase 13A Addendum: Simulated Expert Verification Framework

> [!WARNING]
> SIMULATED_GOLD is a development-only synthetic verification result and is not human-verified ground truth. SIMULATED_EXPERT_LABEL ≠ REAL GROUND TRUTH. SIMULATED reviewer agreement ≠ human inter-rater agreement. Synthetic evaluation does not establish real-world industrial-fire detection accuracy.

## 1. Virtual Reviewer Profiles
To simulate the human evidence-reasoning process, three distinct reviewer profiles were implemented:
- **Reviewer_A_Conservative**: High confidence threshold (0.60) resulting in higher UNKNOWN rates.
- **Reviewer_B_Balanced**: Standard thresholds (0.45).
- **Reviewer_C_Sensitive**: High recall orientation, triggering on weaker evidence signals (0.35 threshold).

Reviewers process isolated evidence packets (Thermal, Behavior, Context, Sentinel). They generate explicit decision rationales (e.g., "High FRP suggests large-scale event") and never have access to `TRUE_SYNTHETIC_CLASS` or latent variables.

## 2. Review Modes and Bias Experiment
- **BLIND Mode**: Reviewers operate entirely independently.
- **MODEL_ASSISTED Mode**: Reviewers are exposed to a simulated B2 prediction with an influence coefficient of 0.25. 
- **Finding**: Exposure to the model prediction caused Reviewer A to alter its original BLIND decision in 15.4% of the events, successfully modeling confirmation bias.

## 3. Simulated Verification Consensus
Out of 76,000 processed events:
- **SIMULATED_GOLD**: 41,699
- **SIMULATED_SILVER**: 15,507
- **SIMULATED_DISPUTED**: 1,073
- **SIMULATED_UNKNOWN**: 17,721

- **Inter-Rater Agreement**: Cohen's Kappa between Reviewer A and Reviewer B was **0.45** (Moderate Agreement).

## 4. Ground Truth Quality Audit
Comparing the `SIMULATED_EXPERT_LABEL` against the generative `TRUE_SYNTHETIC_CLASS` resulted in a **Macro F1 of 34.6%**. This quantifies the profound difficulty of reconstructing overlapping latent physical truths using only observable heuristic rules.

## 5. B2 Multi-Target Evaluation
- When B2 trained against the latent `TRUE_SYNTHETIC_CLASS`, it achieved a training F1 of **~79%**.
- When B2 trained against the `SIMULATED_EXPERT_LABEL`, it achieved a training F1 of **100%**. This perfectly demonstrates how evaluating models against heuristic weak labels drastically overstates performance compared to actual physical truth.

## 6. Real Gold Firewall
- **REAL GOLD Count**: 0. The audit verified that no synthetic labels leaked into the real verified events schema.
