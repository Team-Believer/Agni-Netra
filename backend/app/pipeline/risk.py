from typing import Dict, Any, Tuple

def calculate_risk_index(
    frp_max: float,
    footprint_factor: float,
    duration_hours: float,
    facility_distance_km: float,
    is_critical_facility: bool = False,
    wind_speed_kmh: float = 15.0
) -> Tuple[float, str, Dict[str, float]]:
    """
    Computes the transparent Agni-Netra Risk Index (0 - 100).
    Explicitly labeled as an operational decision-support score,
    not a certified regulatory hazard score.
    """
    # 1. Thermal Intensity Hazard (0 - 35 pts)
    # FRP normalized: 10 MW -> ~5 pts, 100 MW -> ~25 pts, 300+ MW -> 35 pts
    hazard_score = min(35.0, (frp_max / 300.0) * 35.0)

    # 2. Spatial Growth & Footprint Expansion (0 - 25 pts)
    # footprint_factor: 1.0 (static) -> 5 pts, 3.0x -> 20 pts, 4.0x+ -> 25 pts
    growth_score = min(25.0, max(0.0, (footprint_factor - 1.0) * 8.0 + 5.0))

    # 3. Critical Infrastructure & Exposure (0 - 30 pts)
    # Closer to chemical/refinery asset = higher exposure
    if facility_distance_km < 1.0:
        exposure_score = 30.0 if is_critical_facility else 24.0
    elif facility_distance_km < 3.0:
        exposure_score = 22.0 if is_critical_facility else 16.0
    elif facility_distance_km < 5.0:
        exposure_score = 14.0 if is_critical_facility else 10.0
    else:
        exposure_score = 5.0

    # 4. Environmental & Persistence Escalator (0 - 10 pts)
    # Long duration + high wind promotes fire spread
    persistence_score = min(5.0, (duration_hours / 12.0) * 5.0)
    wind_escalator = min(5.0, (wind_speed_kmh / 30.0) * 5.0)
    environmental_score = persistence_score + wind_escalator

    total_risk = round(min(100.0, hazard_score + growth_score + exposure_score + environmental_score), 1)

    if total_risk >= 80.0:
        risk_level = "Critical"
    elif total_risk >= 60.0:
        risk_level = "High"
    elif total_risk >= 35.0:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    contributing_factors = {
        "thermal_intensity_hazard": round(hazard_score, 1),
        "footprint_growth": round(growth_score, 1),
        "infrastructure_exposure": round(exposure_score, 1),
        "persistence_and_wind": round(environmental_score, 1)
    }

    return total_risk, risk_level, contributing_factors
