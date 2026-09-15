# Historical Abnormality Engine

## 1. Purpose
The Historical Abnormality Engine is the production layer answering a single core question: 
> "How different is the current thermal behavior from what is normally expected for this location/event source?"

This engine explicitly **decouples behavior from source**. It does **NOT** answer "Is this a fire?". 
- A known `ROUTINE_FLARE` may be `HIGHLY_ABNORMAL` if its FRP suddenly spikes far beyond its historical limits.
- A `WILDFIRE` may be `NORMAL` if its behavior matches typical seasonal expansion for that location.

## 2. Abnormality Score and States
The module generates a transparent, configurable `ABNORMALITY_SCORE` [0.0 - 1.0]. This score is an evidence/intelligence signal, not a probability or likelihood.

The score determines one of four states:
1. `NORMAL`: The behavior aligns with the established historical baseline.
2. `UNUSUAL`: Moderate deviations in intensity, frequency, spatial extent, or recurrence.
3. `HIGHLY_ABNORMAL`: Significant regime changes, massive FRP spikes, or rapid, uncharacteristic expansions.
4. `UNKNOWN`: Insufficient historical evidence exists to compute an abnormality baseline.

## 3. Configuration & Multi-Dimensional Deviation
The abnormality score is a weighted combination of multiple deviation dimensions, parameterized via `HistoricalAbnormalityConfig`:
- **FRP Deviation**: Current vs Historical FRP.
- **Duration Deviation**: Current event length vs typical historical length.
- **Frequency Deviation**: Detection frequency shifts.
- **Spatial Deviation**: Footprint change and centroid drift.
- **Change Indicators**: Abrupt spikes in FRP or footprint, regime shifts, or activity shifts.

These dimensions preserve interpretability, powering explanations (e.g., "FRP unusually high" rather than just a black-box "Abnormal" label).

## 4. History Tiers & Evidence Completeness
Historical support is segmented into evidence tiers based on availability and baseline robustnes:
- `HISTORY_TIER_A`: High historical recurrence, strong site-specific data.
- `HISTORY_TIER_B`: Moderate site-specific historical data.
- `HISTORY_TIER_C`: Limited history.
- `HISTORY_TIER_D`: Missing history.

If history is missing, the engine evaluates as `UNKNOWN` rather than faking a baseline or assuming `NORMAL`.

## 5. Online vs. Retrospective Isolation
The engine strictly respects operational mode boundaries. 
In `online` mode, it compares the current event prefix against explicitly available historical data *prior* to the current detection sequence. Future observations, ground-truth labels, and retrospective constants (e.g., `final_duration`) are explicitly omitted to prevent data leakage. 

## 6. Pipeline Integration
The Historical Abnormality Engine operates seamlessly in the canonical pipeline:
`EVENT -> CANONICAL FEATURES 1.1 -> LOW-T PERSISTENT -> HISTORICAL ABNORMALITY -> SOURCE CLASSIFIER -> RISK/PRIORITY`

It receives data from the `LOW-T` layer without falsely conflating `LOW_T_PERSISTENT` with `ABNORMAL`. Its outputs form the foundation for downstream risk, priority, and Explanation components (WHY / WHY NOT / WHAT CHANGED).
