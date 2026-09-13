# Agni-Netra Phase 7B: Controlled Historical Acquisition

## Method
Controlled, date-batched historical queries over 3 days using the `VIIRS_SNPP_NRT`, `VIIRS_NOAA20_NRT`, and `VIIRS_NOAA21_NRT` sensors. The bounds strictly isolated India (`68,6,98,36`).

## Validation
- `historical_real/` contains only `REAL_SOURCE` metadata.
- Synthetic files remain completely quarantined.
- No secrets were leaked.

## Next Steps
The pipeline is fully capable of acquiring the complete 90, 180, or 365-day archive safely with rate limiting and retry logic intact, paving the way for unsupervised baseline generation once fully populated.
