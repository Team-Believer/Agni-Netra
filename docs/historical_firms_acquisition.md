# Agni-Netra Phase 7: Historical FIRMS Acquisition

## Purpose
To move away from the invalid synthetic 90-day dataset and acquire genuine historical thermal anomalies for India to train the unsupervised historical baseline engine.

## Authentication Strategy
* The NASA FIRMS API requires an authorized `MAP_KEY` parameter for historical data exceeding 10 days via `https://firms.modaps.eosdis.nasa.gov/api/area/csv/`.
* The acquisition script `src/data/acquire_firms_historical.py` safely inspects the environment for `MAP_KEY` or `FIRMS_MAP_KEY` without logging the value.
* If credentials are missing, the script gracefully aborts to prevent unauthorized access or IP blocking, and preserves all existing datasets.

## Provenance Enforcement
* Historical real data downloaded via this script is saved strictly to `data/raw/firms/historical_real/`.
* Datasets are tagged with `REAL_SOURCE` metadata.
* Synthetic data must remain strictly isolated in `long_window/` and is strictly excluded from `historical_real/`.
