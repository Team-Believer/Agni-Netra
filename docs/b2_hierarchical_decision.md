# Phase 13C Final Report: Hierarchical Decision Architecture

> [!NOTE]
> Optimization improved performance on the deployment-realistic controlled simulation benchmark. REAL-WORLD VERIFIED INDUSTRIAL-FIRE ACCURACY REMAINS UNVALIDATED.

## 1. Hierarchical Design
To combat the excessive conservatism of the Flat B2 model (which had a coverage of only 4.6%), we implemented a Multi-Stage Hierarchical Decision Tree:
- **Level 0**: Evidence Sufficiency check. If `evidence_completeness < 0.3`, immediately output `UNKNOWN`.
- **Level 1**: Macro Class prediction (`Fire-like` vs `Persistent` vs `Unknown`).
- **Level 2**: Sub-class routing (`Industrial Fire` vs `Wildfire` vs `Agricultural Burn`).

## 2. Soft Routing (NEEDS_VERIFICATION)
Rather than blindly routing instances down the tree, we implemented a Soft Routing rule at Level 1. If the probabilities between `Fire-like` and `Persistent` were within 15% of each other (e.g., 0.55 vs 0.45), the model refused to guess and immediately output `UNKNOWN` (Needs Verification).

## 3. Results on Unseen Deployment (Generator C)
Comparing the models on the untouched deployment benchmark:

| Model | Industrial Precision | Industrial Recall | Macro F1 | Coverage |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline 13B (No Abstention)** | 10.7% | 20.3% | 32.6% | 100% |
| **Flat Tuned B2 (Strict Abstention)** | 100.0% | 100.0% | 97.6% | 4.6% |
| **Hierarchical B2 (Soft Routing)** | **60.0%** | **46.1%** | **64.7%** | **9.4%** |

## 4. Final Conclusion
The Hierarchical Model represents the Pareto Optimal operating point. By breaking the problem down into conditional sub-tasks and refusing to route ambiguous cases, it doubled the operational coverage (from 4.6% to 9.4%) compared to the Flat model, while maintaining a highly actionable **60.0% precision** on Industrial Fires (a massive improvement over the 10.7% baseline).
