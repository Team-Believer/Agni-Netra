# Phase 9: B1 Anomaly Engine

## Architecture
The anomaly engine uses a robust univariate deviation method (Median Absolute Deviation) on time-series FRP inputs.
It strictly prevents temporal leakage by calculating baselines using only `T-1` data.

## Scoring Modes
- **Mode A (Retrospective):** Useful for backtesting thresholds.
- **Mode B (Online Temporal):** Validates performance against strictly historical causality.

## Behaviors vs Anomalies
- Behavior mapping evaluates persistence, transience, and intermittency.
- Anomaly scoring is purely a measure of deviation from established baselines, not a fire classifier.
