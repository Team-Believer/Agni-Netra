# Phase 10B: Sentinel-2 Real Raster Corroboration

## Overview
This phase upgrades Phase 10 to extract genuine pixel-based spectral measurements (NDVI, NBR, etc.) using `rasterio` and the public Element84 Earth Search STAC API. 

## Approach
- Bounding boxes are explicitly defined around the FIRMS thermal centroid.
- Geometries are dynamically reprojected into the asset CRS using `pyproj`.
- `rasterio` is used with `AWS_NO_SIGN_REQUEST=True` to attempt to stream Cloud-Optimized GeoTIFFs (COGs) natively from AWS S3 without credentials where publicly permitted by the registry.
- Spectral features and context are mathematically derived exclusively from actual pixels. Zero simulated or fabricated features remain in the pipeline.

## Handling Inaccessibility
- Any asset that is unreachable (e.g. Requester Pays limitations, server errors) is explicitly marked as unavailable/INSUFFICIENT. We never substitute a fabricated record.
