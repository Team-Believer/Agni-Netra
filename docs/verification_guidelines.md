# Agni-Netra Verification Guidelines

## Taxonomy Definition
The following mutually exclusive classes form the strict ground-truth taxonomy. Do not force ambiguous cases into a class; use `Unknown / Insufficient Evidence` if necessary.

1. **Industrial Fire**: Sustained, structurally bound high-heat incidents (e.g., factory fire, pipeline explosion, sustained chemical fire).
2. **Routine Flare / Persistent Industrial Heat**: Non-destructive, operational thermal emissions (e.g., gas flaring, steel mill exhaust, steady-state refinery stacks).
3. **Wildfire**: Uncontrolled vegetation fires in forests, scrublands, or grasslands.
4. **Agricultural Burn**: Controlled, transient fires for crop clearing or field management.
5. **Other Thermal Source**: E.g., volcanic activity, large structural fires that are non-industrial.
6. **Unknown / Insufficient Evidence**: Cases where external evidence is missing, clouded, or temporally mismatched to the FIRMS detection.

## Verification Process
1. **Locate the Event**: Use the `event_id`, latitude, and longitude to locate the thermal anomaly.
2. **Gather External Evidence**:
   - High-resolution optical satellite imagery (e.g., PlanetScope, Maxar, clear Sentinel-2 L2A).
   - Local news reports matching the date and location.
   - Government or emergency response dispatch logs.
3. **Determine the Label Tier**:
   - Assign `GOLD` only if visual evidence clearly confirms the physical nature of the event, or an official report corroborates it.
   - Assign `UNKNOWN` if imagery is cloud-covered and no reports exist.
4. **Record Provenance**:
   - Fill out `verification_source` (e.g., "Sentinel-2 True Color, News Report URL").
   - Fill out `verification_method` (e.g., "Manual optical confirmation").
   - Fill out `review_notes` justifying the classification.

## Critical Warning
Do not rely on the anomaly score or BRONZE label as proof. They are hypotheses to be tested by your independent review.
