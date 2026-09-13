# Long-Window Dataset Authenticity Report (Phase 6B)

## Provenance
**SYNTHETIC.** The 90-day dataset (`data/raw/firms/long_window/firms_90day.csv`) is NOT real NASA FIRMS data.

## Generation Method
The data was artificially expanded from the real 7-day dataset (`data/interim/firms_normalized.csv`) by applying a script (`src/data/expand_dataset.py`) that explicitly used:
1. **Date shifting**: Copied existing observations backward in time up to 90 days.
2. **Pandas replication**: Duplicated coordinates exactly.
3. **Random FRP modification**: Synthetically altered the Fire Radiative Power by a uniform multiplier between 0.8 and 1.2 to simulate realistic variance.

## Invalid Claims Retracted
* **"919 geographic locations have >50 observations over 90 days."** — This is purely a mathematical artifact of the duplication script intentionally duplicating 10% of the dataset with an 80% survival rate per day. This does NOT reflect physical reality.
* **Historical Fingerprinting Readiness** — Since the data is synthetic, we CANNOT use it to build robust baseline signatures of physical industrial sites.

## Dataset Usage Policy
The 90-day expanded dataset MUST NOT be used to train or evaluate the final anomaly detection system. It is strictly a software engineering artifact for pipeline stress testing. 

## Legitimate Data Acquisition
To obtain *real* 90-day data, the project requires an active API token for the NASA LANCE / FIRMS API (specifically the `https://firms.modaps.eosdis.nasa.gov/api/area/csv/` endpoint) passing a valid MAP_KEY, bounding box, and the requested historical date range. Without this token, historical queries exceeding 10 days are blocked.
