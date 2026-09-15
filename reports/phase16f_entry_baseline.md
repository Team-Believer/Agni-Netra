# Phase 16F Entry Baseline

## Frozen Configurations
- **Selected Model**: Stage-Gated Pareto Candidate (GlobalSourceGRU + XGB Meta Fusion)
- **Frozen Feature Schema**: Multi-stream explicit + Neural OOF Logits
- **Frozen Dropout Rate**: 0.1
- **Frozen Decorrelation Level**: MODERATE
- **Frozen Hard Negative Ratio**: 2.0
- **Frozen Class Weighting**: BALANCED
- **Exact Frozen Threshold**: 0.1875

## Frozen Baseline Metrics
- ID Macro F1: 0.1981
- OOD Macro F1: 0.3014
- Worst-Case F1: 0.1981
- Industrial Fire ID Precision: 0.2655
- Industrial Fire ID Recall: 0.4261
- Industrial Fire ID F1: 0.3272
- Industrial Fire OOD Precision: 0.0974
- Industrial Fire OOD Recall: 0.5926
- Industrial Fire OOD F1: 0.1673

## Blind Evaluation
- Generator D Result: Macro F1: 0.1160 | IF Precision: 0.0058 | IF Recall: 0.1667 | IF F1: 0.0111
