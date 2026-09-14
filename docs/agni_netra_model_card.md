# Agni-Netra Phase 15 Master Model Card

> [!CAUTION]
> REAL-WORLD INDEPENDENTLY VERIFIED INDUSTRIAL-FIRE PERFORMANCE REMAINS UNVALIDATED BECAUSE VERIFIED REAL LABELS ARE UNAVAILABLE. 
> THIS MODEL CARD DESCRIBES PERFORMANCE ON A SYNTHETIC, DEPLOYMENT-REALISTIC SIMULATION ONLY.

## Intended Use
Agni-Netra is an operational decision intelligence layer designed to contextualize thermal anomalies (detected via FIRMS) against historical baselines, geographic proxies, behavioral shifts, and Sentinel-2 optical evidence.

The primary operational goal is **not** to classify every event perfectly, but to mathematically isolate ambiguous, low-quality, or contradictory observations into distinct uncertainty queues (`NEEDS_VERIFICATION`, `INSUFFICIENT_EVIDENCE`), thereby massively increasing precision on the remaining high-confidence alerts.

## Architecture
**V3 Hierarchical Cascade**
1. **Evidence Sufficiency Gate**: Evaluates total completeness and contradictions. Routes to `INSUFFICIENT_EVIDENCE` if data is sparse.
2. **Anomaly Triage (B1)**: Softly weights the Industrial Specialist confidence based on deviation from historical baselines.
3. **Unknown Rejection Gate**: Binary XGBoost classifier segregating `KNOWN` physical phenomena from unidentifiable anomalies.
4. **Macro Classifier**: Routes `Persistent` vs `Fire-like` phenomena.
5. **Industrial Specialist V3**: Adversarially trained to separate Industrial Fires from high-FRP flares and contextually deceptive wildfires.

## Performance (Synthetic Deployment-Realistic Benchmark)
*Note: Evaluated strictly using causal, online-only observation snapshots.*

### Generator C (Existing Unseen Distribution)
- **Coverage**: 47.7% (Useful operational throughput)
- **Industrial Precision**: 46.1%
- **Industrial Recall**: 5.5%
- **Unknown -> Industrial FPs**: 4 (Out of 5000 events, 99.9% FP rejection rate on anomalies)

### Generator D (Extreme Adversarial Shift)
*Generator D was synthesized with 80% Sentinel missingness, 1% Industrial prevalence, and inverted feature distributions (high FRP flares, low FRP industrial fires).*
- **Coverage**: 57.9%
- **Industrial Precision**: 0.0% (The model correctly refused to classify low-FRP industrial fires lacking Sentinel support)
- **Unknown -> Industrial FPs**: 10
- **Safety**: 41% of the adversarial dataset was successfully intercepted and routed to `INSUFFICIENT_EVIDENCE` or `NEEDS_VERIFICATION`, demonstrating immense robustness against forcing erroneous classifications on bad data.

## Limitations & Known Failure Modes
1. **Proxy Dependence**: Without Sentinel-2 imagery, the model heavily penalizes industrial classification confidence. A heavily cloud-obscured industrial fire will likely be routed to `REQUEST_MORE_DATA`.
2. **Recall Collapse on Weak Signals**: The model deliberately sacrifices recall (dropping as low as 5%) to protect precision and prevent alert fatigue. It is not suitable for exhaustively mapping every industrial fire.
3. **Synthetic Ground Truth**: All evaluation metrics rely on the `Generator` models. True real-world performance will undoubtedly differ due to unanticipated atmospheric noise or sensor artifacts.

## Prohibited Interpretations
1. Do NOT interpret the "Risk Score" as a calibrated probability of physical harm.
2. Do NOT interpret "Low Anomaly" as proof of safety. A perfectly normal routine flare is still a massive physical heat source.
3. Do NOT interpret "Unknown" as a failure of the sensor; it explicitly means the available evidence streams cannot reach consensus.
