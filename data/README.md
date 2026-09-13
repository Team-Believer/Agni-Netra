# Agni-Netra Phase 2 FIRMS Dataset

## Acquisition Strategy
This dataset contains a 7-day rolling archive of active fire detections for South Asia, obtained directly from the public NASA FIRMS API.
It includes observations from the **VIIRS S-NPP** (Sensor N) and **VIIRS NOAA-20** (Sensor N20) satellites (375m spatial resolution).

## Reason for Selection
Because no local `MAP_KEY` credentials were found in the environment, we fell back to the official unauthenticated 7-day CSV URLs provided by NASA FIRMS. This provides a small but highly relevant dataset covering India, sufficient for Phase 2 inspection, schema validation, and developing the B0 ML baseline.

## Data Structure
- `data/raw/firms`: Contains the original immutable downloaded CSV files (`suomi_npp_viirs_south_asia_7d.csv`, `noaa_20_viirs_south_asia_7d.csv`) and a `metadata.json` tracking acquisition parameters.
- `data/interim/firms_normalized.csv`: A unified and normalized observation-level dataset (9714 rows).

## Schema Documentation
- `latitude`, `longitude`: Coordinate location of the thermal anomaly (float).
- `bright_ti4`: VIIRS I-4 band brightness temperature of the fire pixel (float).
- `scan`, `track`: Spatial resolution of the observation.
- `acq_date`, `acq_time`: UTC Date and Time of acquisition.
- `satellite`: Satellite indicator (`N` for S-NPP, `N20` for NOAA-20).
- `confidence`: Detection confidence (`low`, `nominal`, `high`).
- `version`: Product version (e.g., `2.0NRT`).
- `bright_ti5`: VIIRS I-5 band brightness temperature (float).
- `frp`: Fire Radiative Power in MW (float).
- `daynight`: `D` (Day) or `N` (Night) observation.

## Data Quality
- **Invalid coords:** 0
- **Invalid FRP:** 0
- **Missing Data:** 0% missing across core fields.

## Spatial Analysis
- **Geographic bounds:** Lat [5.5, 39.9], Lon [54.0, 101.9] (covers all of India).
- **Density:** High density. Out of a 10,000-point sample, the **median nearest neighbor distance is just 0.15 km** (150 meters).
- **Clusters:** 7,995 points have another point within 1 km, strongly suggesting massive spatial clustering due to persistent industrial activity, multi-pixel fire fronts, or repeated satellite passes over the same facility.

## Temporal Analysis
- **Temporal bounds:** 2026-09-06 to 2026-09-13
- **Day/Night Split:** 5506 Night (`N`), 4208 Day (`D`).
- **Persistence:** High likelihood of persistence given the density and day/night split, meaning stationary industrial flares will be repeatedly observed day and night.

## Sensor Comparison
- **NOAA-20 (N20):** 5114 observations
- **S-NPP (N):** 4600 observations
Both satellites provide highly complementary data. The combined detections provide high temporal resolution for detecting persistent sources.
