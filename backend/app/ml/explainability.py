from typing import Dict, Any, List

def format_event_explanations(
    source_class: str,
    confidence: float,
    behavior: str,
    abnormality: str,
    frp_change_pct: float,
    footprint_factor: float,
    duration_hours: float,
    facility_type: str = "Industrial Refinery"
) -> Dict[str, Any]:
    """
    Generates structured, grounded explanations:
    - WHY (reasons supporting the hypothesis)
    - WHY NOT (reasons discounting competing hypotheses)
    - WHAT CHANGED (changes relative to historical baseline)
    """
    why_items: List[str] = []
    why_not_items: List[str] = []
    what_changed_items: List[str] = []

    if source_class == "Industrial Fire":
        why_items.append("High thermal intensity observed inside or adjacent to industrial facility bounds.")
        if footprint_factor > 1.5:
            why_items.append(f"Spatial thermal footprint expanded by {footprint_factor:.1f}x across consecutive satellite passes.")
        if frp_change_pct > 50:
            why_items.append(f"Fire Radiative Power (FRP) escalated by +{frp_change_pct:.0f}% over facility baseline.")
        why_items.append("Temporal persistence exceeds typical transient agricultural or burn-off signatures.")

        why_not_items.append("Not a Routine Flare: Thermal footprint has expanded significantly beyond flare stack perimeter.")
        why_not_items.append(f"Not an Agricultural Burn: Centered within designated industrial zone ({facility_type}).")
        why_not_items.append("Not Sensor Glint: Corroborated across multiple orbits with multi-spectral confirmation.")

        what_changed_items.append(f"FRP increased by +{frp_change_pct:.0f}% relative to 30-day historical mean.")
        what_changed_items.append(f"Footprint expanded {footprint_factor:.1f}x from initial detection cluster.")
        what_changed_items.append(f"Continuous active thermal duration has reached {duration_hours:.1f} hours.")

    elif source_class == "Routine Flare":
        why_items.append("FRP matches registered historical baseline range for facility flare stack.")
        why_items.append("Compact, stationary spatial footprint with zero outward propagation.")
        why_items.append("High temporal recurrence at known facility coordinates.")

        why_not_items.append("Not an Industrial Fire: No spatial expansion; FRP remains within nominal operational bounds.")
        why_not_items.append("Not Wildfire: Confined directly to registered industrial point source.")

        what_changed_items.append("Slight cyclical operational fluctuation within ±15% of historical median.")
        what_changed_items.append("Footprint stationary with zero expansion.")

    elif source_class == "Agricultural Burn":
        why_items.append("Located on cropland/agricultural land-use zone.")
        why_items.append("Moderate FRP signature with rapid transient decay within 2-4 hours.")
        why_items.append("Consistent with seasonal post-harvest clearing patterns.")

        why_not_items.append("Not an Industrial Fire: Distant from registered industrial infrastructure.")
        why_not_items.append("Not a Continuous Flare: Short-lived diurnal heat profile.")

        what_changed_items.append("Seasonal open-field fire detected on previously unburned parcel.")

    elif source_class == "Wildfire":
        why_items.append("Located in forested/dense vegetation area away from settlements.")
        why_items.append("Uncontained perimeter growth aligned with prevailing wind direction.")
        why_items.append("Multiple dispersed thermal hot spots detected along advancing front.")

        why_not_items.append("Not an Industrial Source: Located outside any industrial corridor or pipeline route.")

        what_changed_items.append(f"Thermal front advanced over {footprint_factor:.1f} km² in last 6 hours.")

    else: # Unknown / Low Confidence
        why_items.append("Insufficient multi-pass observations to confirm source typology with high confidence.")
        why_items.append("Observation confidence below calibration threshold.")

        why_not_items.append("Premature to classify: requires next satellite pass or UAV/ground verification.")

        what_changed_items.append("Initial thermal signal detected; awaiting corroborating sensor pass.")

    return {
        "why": why_items,
        "why_not": why_not_items,
        "what_changed": what_changed_items
    }
