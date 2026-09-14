# Phase 13B Final Report: Deployment-Realistic Synthetic Validation

> [!WARNING]
> This is a real-data-anchored controlled simulation benchmark. This benchmark is designed to approximate deployment conditions using empirical real-data distributions. Synthetic hidden labels are not independently verified real-world ground truth. Performance on this benchmark does not establish real-world industrial-fire detection accuracy. REAL_GOLD remains unavailable.

## 1. Real-Data Distribution Profile
The generative model extracted empirical marginals (quantiles) and Spearman rank correlations directly from `events_90d/events.csv`. 
- **Generated Benchmark Size**: 75,000 deployment events.
- **Generator Splitting**: Generator A (47k Train, 12k Test), Generator B Shift (10k), Generator C Unseen (5k).

## 2. Generative Independence & Online Simulation
Latent trajectories were modeled first. Then, observation prefixes (`T0...T_current`) were exposed strictly without leaking `final_frp` or `final_duration` to the Online model. `TRUE_DEPLOYMENT_SIM_CLASS` was assigned based on the generative taxonomy, NOT by copying heuristic BRONZE labels.

## 3. Real vs Synthetic Similarity Audit
- **FRP KS-Statistic**: 0.14
- **Correlation Divergence (FRP vs Duration)**: 0.18
- **Conclusion**: The simulation successfully reconstructs real-world marginal scales and rank dependence without rigidly copying exact samples.

## 4. Advanced B2 Evaluation (Models G & H)
- **Model H (Retrospective - Final Evidence)**: Achieved a Macro F1 of **40.6%** on Test A (Facility Holdout).
- **Model G (Online Prefix - Current Evidence)**: Achieved a Macro F1 of **34.4%** on Test A.
  - This 6% gap quantifies the "Decision Latency" challenge. Early observations are vastly harder to classify than completed events.

## 5. Generator Shift and Unseen Deployment Tests
- On **Generator B (Shift)**, Online F1 dropped to **33.7%**.
- On **Generator C (Unseen Deployment)**, Online F1 dropped to **32.6%**. 
- **Industrial Fire Precision (Test C)**: **10.7%** (with an FPR of 9.7%). This brutally realistic metric reveals the true difficulty of separating industrial operations from overlapping agricultural and wildfire events during live operational streams.

## 6. Abstention and Calibration
The B2 confidence distributions were analyzed on Test C:
- Operating at a **0.50 confidence threshold**: Coverage is 24%, Selective Macro F1 is 39%.
- Operating at a **0.90 confidence threshold**: Coverage collapses to **3.1%**, but Selective Macro F1 surges to **71.4%**.
- **Conclusion**: Risk-sensitive deployment requires aggressive abstention. The system must abstain on ~90% of ambiguous early-stage events to maintain actionable precision for automated alerts.

## 7. Firewall Status
The Audit strictly confirmed that `label_tier = DEPLOYMENT_SIMULATED` is used exclusively, and the count of `REAL_GOLD` verified events remains exactly **0**.

## Final Classification
- **REAL-WORLD VERIFIED ACCURACY**: NOT ESTABLISHED
- **DEPLOYMENT-REALISTIC SYNTHETIC VALIDATION**: ESTABLISHED
