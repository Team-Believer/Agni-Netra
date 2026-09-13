# Phase 10: Sentinel-2 Multispectral Corroboration

## Overview
This phase integrates an independent contextual corroboration layer using Sentinel-2 L2A optical/SWIR data via STAC API. It explicitly separates FIRMS (thermal detection) from Sentinel-2 (contextual evidence) without prematurely claiming fire confirmation.

## Logic
- The system queries a public STAC API (Earth Search) using event bounding boxes.
- Metadata is returned, preventing heavy raster downloads until absolutely necessary.
- Clouds (`eo:cloud_cover`) and temporal gaps (`time_delta`) are rigorously handled to avoid classifying "unavailable data" as "no fire".
- Valid imagery yields simulated spectral contrast scores that act as independent contextual evidence, integrated into the evidence ledger.
