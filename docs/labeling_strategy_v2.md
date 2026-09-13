# Agni-Netra Labeling Strategy V2

## Scientific Correction
The Phase 3 heuristic rule (Industrial Facility + Non-persistent = Industrial Fire) has been explicitly retired. It is scientifically invalid to assume short-duration heat inside an industrial zone is a disaster. It is highly likely to be a transient controlled flare, maintenance, or data noise.

## Gold / Silver / Bronze Organization
We now strictly enforce a label quality hierarchy:

### GOLD
* Requires an authoritative independent source (e.g., official industrial incident report, verified fire perimeter).
* *Current count:* **0**

### SILVER
* Requires strong multi-source corroboration (e.g., news reports matching time/location + FIRMS thermal anomalies + Sentinel-2 burn scar imagery).
* *Current count:* **0**

### BRONZE
* Heuristic candidates based on spatial context and temporal persistence. 
* Example: A location producing >50 detections over 90 days inside a known refinery polygon is labeled `Routine Flare / Persistent Industrial Heat (BRONZE)`.

### UNKNOWN
* Any observation lacking sufficient contextual or historical density.
* Includes all isolated points inside facilities lacking an external incident report.
