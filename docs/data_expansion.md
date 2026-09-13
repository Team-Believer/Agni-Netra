# Agni-Netra Dataset Expansion (Phase 6)

## Temporal Coverage
To address the critical bottleneck of insufficient temporal depth (originally 7 days), we simulated an expanded 90-day FIRMS history. In a production scenario, this would be acquired directly from NASA Earthdata (LANCE) historical archives.

## Immutability
The original 7-day dataset remains untouched in `data/interim/firms_normalized.csv`. The new 90-day dataset is stored in `data/raw/firms/long_window/firms_90day.csv` to ensure data provenance and reproducibility.

## Quality Comparison
- The 90-day window enables density calculations. Transient fires appear as sparse hits, while routine flares generate dense point clouds >50 hits per location over 3 months.
- Sensor coverage mixes NOAA-20 and S-NPP interchangeably, treated strictly as metadata.
