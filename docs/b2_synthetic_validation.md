# Phase 13A Final Report: Advanced B2 Validation on Controlled Synthetic Reference Dataset

> [!WARNING]
> Synthetic evaluation validates implementation, controlled learning behavior, robustness, and end-to-end pipeline correctness; it does not establish real-world industrial-fire detection accuracy.

## Dataset & Generative Profile
- **A. Synthetic dataset size**: 75,000 generated target events plus 1,000 paired counterfactual/hard-case events.
- **B. Class distribution**: Explicitly balanced input probabilities (15-20% per class).
- **C. Environment distribution**: 7 overlapping proxy environments generating realistic cross-class ambiguity.
- **D. Scenario distribution**: Generator A (60,000) and Generator B (15,000) for distinct parameter shifts.
- **E. Latent-variable design**: Utilized 5 core latent states including `day_night_bias` and `thermal_intensity_mu` to govern observables.
- **F. Noise & Missingness**: Sentinel-2 simulation injected 10% total missingness and up to 99% cloud fractional masking for hard cases.
- **G. Online vs Retrospective**: Sentinel features were strictly nullified if `time_delta_hours > 0`.

## Model Evaluation Results
- **Q/R. Macro F1 & Balanced Accuracy**:
  - Model B (Full Evidence): **67.9% F1** (68.3% Balanced Acc)
- **X. Sentinel Ablation**:
  - Removing Sentinel-2 (Model C) resulted in **66.8% F1**, confirming Sentinel provides a small but measurable ~1.1% gain in distinguishing overlapping thermal profiles.
- **Y. Proxy Ablation**:
  - Removing Geographic/Environmental Proxies (Model E) resulted in **59.9% F1**. This 8% drop proves the model still relies heavily on geographic context, though the synthetic overlap prevented the total collapse seen in Phase 11.
- **Z. Generator Shift Generalization**:
  - Training on Generator A and testing on Generator B resulted in **62.0% F1**. The model successfully generalized beyond the exact parameter state of Generator A, though it suffered a ~6% degradation.

## Final Decisions
1. **Is B2 implementation mature?** Yes. The architecture successfully handles missingness, abstention, and feature separation.
2. **Is B2 robust?** Moderately. It survived the Generator B shift test reasonably well.
3. **Does Sentinel materially help?** Yes, slightly (~1.1% F1 boost).
4. **Does B2 depend on contextual proxies?** Yes. Losing the proxy context dropped performance by 8 points.
5. **What parts are validated synthetically?** The entire machine learning architecture, missingness handling, and proxy-ablation measurement.
6. **What remains completely unvalidated in the real world?** The actual, physical decision boundary separating real industrial fires from routine flares. REAL-WORLD VERIFIED INDUSTRIAL-FIRE PERFORMANCE: **NOT ESTABLISHED.**

**Recommended Phase 14**: Transition to integrating the unsupervised B1 Anomaly Engine with the B2 architecture into a unified risk scoring system, or deploy the system in a monitoring shadow mode.
