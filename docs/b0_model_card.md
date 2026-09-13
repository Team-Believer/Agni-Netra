# Agni-Netra B0 Baseline Model Card

## Purpose
This model establishes the mechanics of the Agni-Netra Machine Learning pipeline. It proves that our preprocessing, feature engineering, label mapping, XGBoost GPU integration, and deterministic inference schemas function correctly.

## Intended Use
- **Development Diagnostic Only:** To test the data pipeline architecture.
- **NOT intended use:** This model MUST NOT be used for real-world inference, scientific benchmarking, or generalized evaluation of accuracy.

## Training Data & Label Quality
- **Training Samples:** 40 weakly-labeled events out of 3,302 total events.
- **Label Status:** ZERO `VERIFIED` labels. All labels are `WEAK` provisional labels heuristically derived from OSM spatial intersection.
- **Imbalance:** 30 Industrial Fires, 4 Agricultural Burns, 3 Wildfires, 3 Flares.
- **Missingness:** 3,262 `UNKNOWN` events were intentionally excluded from supervised training to prevent corrupting the class targets.

## Model
- **Algorithm:** XGBoost (`multi:softprob`).
- **Hardware:** Trained locally (capable of falling back from CUDA to CPU if GPU memory is constrained or drivers are misconfigured).
- **Mode:** MODE A (Pipeline Smoke Test). We did NOT perform a Train/Test split because 40 highly imbalanced weak samples cannot produce a statistically valid generalization holdout.

## Feature Groups Used
- **THERMAL:** FRP and Brightness metrics.
- **TEMPORAL:** Durations, Gaps, Counts.
- **SPATIAL:** Spread.
- **BEHAVIOR:** Expansion, Stability, FRP spikes.
- *Strictly Target-Independent: No label or context data was leaked into features.*

## Known Limitations and Biases
1. **Lack of Verified Ground Truth:** We are essentially teaching the model to reverse-engineer our heuristic OSM-intersection rules rather than predicting physical reality.
2. **Retrospective Nature:** This model relies on offline features (`duration_hours`, `max_frp` of the full event lifetime) and cannot be applied in real-time at the moment of first detection.
3. **Overfitting:** Because we trained on the entire valid subset (40 events) simply to smoke-test the pipeline, training accuracy will approach 100% (extreme overfitting).

## Evaluation Methodology
Why current metrics are not production benchmarks:
Without a `VERIFIED` test set, any F1 score calculation is scientifically invalid. We only evaluate the training set to verify that the model compiles, optimizes, and converges successfully.
