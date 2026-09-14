# Synthetic Reference Dataset Pipeline

## 1. Overview
This dataset contains 75,000 synthetic events explicitly generated to stress-test the B2 classifier.
**IMPORTANT:** This is NOT real-world ground truth and cannot be used to establish real-world industrial-fire detection accuracy.

## 2. Generative Process
- **Latent Model**: Maps 6 classes and 7 environments into overlapping latent variables (`thermal_intensity_mu`, `vegetation_proxy`, etc.).
- **Observable Features**: Samples features (FRP, duration, NDVI) with configurable measurement noise.
- **Missingness**: Explicitly models Sentinel-2 cloud cover and data unavailability (NaN injection).

## 3. Strict Data Firewalls
- The label is strictly named `TRUE_SYNTHETIC_CLASS` and `SIMULATED_WEAK_LABEL_20`.
- Anti-Cheating protocols successfully proved that `TRUE_SYNTHETIC_CLASS`, `latent_source_type`, and `generation_rule_id` were not passed to the models and that no single observable feature exceeded a 0.90 correlation with the target class.

## 4. Counterfactual Pairs
A controlled set of pairs was generated (`synthetic_counterfactuals.csv`) where only the geographic environment proxies were altered, preserving the identical thermal signal, to test model sensitivity to context shifts.
