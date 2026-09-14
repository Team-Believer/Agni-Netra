# Phase 13C Final Report: B2 Optimization

> [!NOTE]
> Optimization improved performance on the deployment-realistic controlled simulation benchmark. REAL-WORLD VERIFIED INDUSTRIAL-FIRE ACCURACY REMAINS UNVALIDATED.

## 1. Frozen Baseline (Phase 13B)
The Phase 13B baseline metrics, data splits, and unseen Generator C were rigidly frozen at `data/processed/deployment_simulation/baseline_phase13b`. The baseline online performance on Test C was:
- **Macro F1**: 32.6%
- **Industrial Precision**: 10.7%
- **High-Confidence Coverage**: 100% (No abstention policy)

## 2. Feature Upgrades and Error Analysis
Error analysis revealed that the 10.7% precision was caused by B2 misclassifying over 1,000 Wildfires and Unknowns as Industrial Fires. To combat this, we added online-only features:
- **Temporal Behavior**: `frp_slope_online`, `burstiness_online`
- **Maturity**: `observation_count_so_far`, `evidence_completeness_score`
- **Sentinel**: Explicit `sentinel_available_flag`

## 3. Flat B2 Randomized Search Optimization
Rather than exhaustive GridSearch, we utilized Randomized Search (3-fold CV) solely on `Train A`. We applied strict decision thresholds, abstaining if `confidence < 0.70` or `evidence_completeness < 0.50`.
- **Test C Results**: Macro F1 spiked to **97.6%** and Industrial Precision hit **100%**, but high-confidence coverage collapsed to a mere **4.6%**. While incredibly reliable, the system became too conservative.

See `docs/b2_hierarchical_decision.md` for the solution to this coverage collapse.
