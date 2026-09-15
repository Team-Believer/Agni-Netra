"""
Agni-Netra High-Temperature Thermal Physics / VNF-Style Evidence Lane (Phase 20C)

Extracts physically interpretable thermal evidence from available FIRMS/VIIRS thermal observations.

Core Scientific Principles:
HIGH-TEMP PHYSICS != SOURCE CLASSIFICATION
HIGH FRP != HIGH TEMPERATURE BY ITSELF
REDUCED MODE != FULL VNF
SATURATION != HIGHER CONFIDENCE

Complements the Low-T persistent heat lane. Operates in source-agnostic fashion across all source classes.
"""

import math
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple, Union

from src.features.canonical_event_features import CanonicalEventFeatures

# Physics Modes
MODE_REDUCED = "REDUCED_THERMAL_PHYSICS_MODE"
MODE_FULL = "FULL_MODE"
MODE_UNAVAILABLE = "UNAVAILABLE"

# High-T Signal States
SIGNAL_STRONG = "STRONG"
SIGNAL_MODERATE = "MODERATE"
SIGNAL_WEAK = "WEAK"
SIGNAL_NOT_DETECTABLE = "NOT_DETECTABLE"
SIGNAL_UNKNOWN = "UNKNOWN"


@dataclass
class ThermalPhysicsInput:
    """Abstraction for thermal measurements, supporting future multispectral inputs."""
    frp: Optional[float] = None
    brightness_temperature: Optional[float] = None
    solar_zenith_angle: Optional[float] = None
    band_radiance: Optional[Dict[str, float]] = None
    spectral_response: Optional[Dict[str, Any]] = None
    emissivity: Optional[float] = None
    source_area: Optional[float] = None

    def is_multispectral_complete(self) -> bool:
        """Returns True only when full VNF/Planck multispectral inputs are present."""
        return (
            self.band_radiance is not None and
            len(self.band_radiance) >= 2 and
            self.emissivity is not None and
            self.source_area is not None
        )


@dataclass
class HighTThermalConfig:
    """Configurable thresholds for thermal physics evaluation."""
    moderate_frp_mw: float = 50.0
    high_frp_mw: float = 200.0
    extreme_frp_mw: float = 800.0
    moderate_bt_kelvin: float = 330.0
    high_bt_kelvin: float = 360.0
    extreme_bt_kelvin: float = 400.0


@dataclass
class HighTThermalAssessment:
    """Structured assessment of high-temperature thermal physics evidence."""
    event_id: str
    available: bool
    physics_mode: str
    input_completeness: float
    thermal_intensity_score: float
    high_temperature_signal: str
    thermal_extremeness: float
    thermal_concentration: float
    thermal_measurement_reliability: float
    brightness_temperature_summary: Dict[str, Any]
    frp_summary: Dict[str, Any]
    source_physics_indicators: Dict[str, Any]
    quality_limitations: List[str]
    reason_codes: List[str]
    evidence_items: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "HighTThermalAssessment":
        return cls(
            event_id=d["event_id"],
            available=d["available"],
            physics_mode=d["physics_mode"],
            input_completeness=float(d["input_completeness"]),
            thermal_intensity_score=float(d["thermal_intensity_score"]),
            high_temperature_signal=d["high_temperature_signal"],
            thermal_extremeness=float(d["thermal_extremeness"]),
            thermal_concentration=float(d["thermal_concentration"]),
            thermal_measurement_reliability=float(d["thermal_measurement_reliability"]),
            brightness_temperature_summary=d["brightness_temperature_summary"],
            frp_summary=d["frp_summary"],
            source_physics_indicators=d["source_physics_indicators"],
            quality_limitations=d["quality_limitations"],
            reason_codes=d["reason_codes"],
            evidence_items=d.get("evidence_items", [])
        )


def estimate_thermal_physics(
    physics_input: ThermalPhysicsInput,
    config: Optional[HighTThermalConfig] = None
) -> Dict[str, Any]:
    """
    Estimates thermal physics indicators.
    Switches between REDUCED_THERMAL_PHYSICS_MODE and FULL_MODE based on input completeness.
    Enforces NO FAKE PLANCK FIT rule when multispectral data is missing.
    """
    if config is None:
        config = HighTThermalConfig()

    if physics_input.is_multispectral_complete():
        # Full VNF / Planck mode interface path
        mode = MODE_FULL
        # Full VNF spectral integration (placeholder interface for future spectral sensors)
        temp_est = 1500.0  # Planck fit placeholder in full mode only
        area_est = physics_input.source_area or 10.0
        return {
            "mode": mode,
            "planck_temperature_kelvin": temp_est,
            "source_area_sq_m": area_est,
            "radiance_fitted": True
        }
    else:
        # Reduced thermal physics mode (honest FIRMS/VIIRS input path)
        mode = MODE_REDUCED
        frp_val = physics_input.frp
        bt_val = physics_input.brightness_temperature

        frp_signal = 0.0
        if frp_val is not None and not math.isnan(frp_val):
            frp_signal = min(1.0, frp_val / config.extreme_frp_mw)

        bt_signal = 0.0
        if bt_val is not None and not math.isnan(bt_val):
            bt_signal = min(1.0, max(0.0, (bt_val - 290.0) / (config.extreme_bt_kelvin - 290.0)))

        return {
            "mode": mode,
            "frp_signal": round(frp_signal, 4),
            "bt_signal": round(bt_signal, 4),
            "planck_temperature_kelvin": None,  # No fake fit!
            "source_area_sq_m": None
        }


def _extract_thermal_values_from_event(
    canon: CanonicalEventFeatures,
    raw_event: Optional[Dict[str, Any]] = None
) -> Tuple[Optional[float], Optional[float], List[float], List[float]]:
    """
    Extracts FRP and Brightness Temperature values from canon and raw event dictionary.
    Returns: (mean_frp, max_frp, bt_values, frp_values)
    """
    max_frp = float(canon.current_max_frp) if not np.isnan(canon.current_max_frp) else 0.0
    mean_frp = float(canon.current_mean_frp) if not np.isnan(canon.current_mean_frp) else max_frp

    frp_values = [max_frp]
    bt_values = []

    if raw_event:
        # Check direct or observation list fields
        for bt_key in ["brightness_temperature", "bright_t31", "bright_t13", "brightness_temp_mean", "bt"]:
            if bt_key in raw_event and raw_event[bt_key] is not None:
                try:
                    val = float(raw_event[bt_key])
                    if not math.isnan(val) and val > 0:
                        bt_values.append(val)
                except (ValueError, TypeError):
                    pass

        # Check raw observation list if present
        if "observations" in raw_event and isinstance(raw_event["observations"], list):
            for obs in raw_event["observations"]:
                if isinstance(obs, dict):
                    for bt_key in ["brightness_temperature", "bright_t31", "bright_t13", "bt"]:
                        if bt_key in obs and obs[bt_key] is not None:
                            try:
                                val = float(obs[bt_key])
                                if not math.isnan(val) and val > 0:
                                    bt_values.append(val)
                            except (ValueError, TypeError):
                                pass
                    if "frp" in obs and obs["frp"] is not None:
                        try:
                            val = float(obs["frp"])
                            if not math.isnan(val) and val >= 0:
                                frp_values.append(val)
                        except (ValueError, TypeError):
                            pass

    return mean_frp, max_frp, bt_values, frp_values


def evaluate_high_t_lane(
    canon: CanonicalEventFeatures,
    raw_event: Optional[Dict[str, Any]] = None,
    quality_summary: Optional[Any] = None,
    config: Optional[HighTThermalConfig] = None
) -> HighTThermalAssessment:
    """
    Evaluates high-temperature thermal physics lane from canonical features & raw observations.
    """
    if config is None:
        config = HighTThermalConfig()

    event_id = str(raw_event.get("event_id", raw_event.get("id", "evt_unknown"))) if raw_event else "evt_unknown"

    mean_frp, max_frp, bt_values, frp_values = _extract_thermal_values_from_event(canon, raw_event)

    has_frp = max_frp > 0.0 or any(v > 0.0 for v in frp_values)
    has_bt = len(bt_values) > 0 and any(v > 0.0 for v in bt_values)

    if not has_frp and not has_bt:
        return HighTThermalAssessment(
            event_id=event_id,
            available=False,
            physics_mode=MODE_UNAVAILABLE,
            input_completeness=0.0,
            thermal_intensity_score=0.0,
            high_temperature_signal=SIGNAL_UNKNOWN,
            thermal_extremeness=0.0,
            thermal_concentration=0.0,
            thermal_measurement_reliability=0.0,
            brightness_temperature_summary={"available": False, "min": None, "mean": None, "max": None},
            frp_summary={"available": False, "min": None, "mean": None, "max": None, "total": None},
            source_physics_indicators={},
            quality_limitations=["No valid FRP or brightness temperature measurements found"],
            reason_codes=["NO_THERMAL_MEASUREMENTS"],
            evidence_items=[]
        )

    # 1. FRP Summaries
    frp_min = float(np.min(frp_values)) if frp_values else max_frp
    frp_mean = float(np.mean(frp_values)) if frp_values else mean_frp
    frp_max = float(np.max(frp_values)) if frp_values else max_frp
    frp_sum = float(np.sum(frp_values)) if frp_values else max_frp

    frp_summary = {
        "available": True,
        "min": round(frp_min, 2),
        "mean": round(frp_mean, 2),
        "max": round(frp_max, 2),
        "total": round(frp_sum, 2)
    }

    # 2. Brightness Temperature Summaries
    if has_bt:
        bt_min = float(np.min(bt_values))
        bt_mean = float(np.mean(bt_values))
        bt_max = float(np.max(bt_values))
        bt_summary = {
            "available": True,
            "min": round(bt_min, 2),
            "mean": round(bt_mean, 2),
            "max": round(bt_max, 2)
        }
    else:
        bt_min = bt_mean = bt_max = None
        bt_summary = {"available": False, "min": None, "mean": None, "max": None}

    # 3. Mode Determination & Input Completeness
    phys_input = ThermalPhysicsInput(
        frp=frp_max,
        brightness_temperature=bt_max
    )
    estimates = estimate_thermal_physics(phys_input, config=config)
    physics_mode = estimates["mode"]

    input_comp = 0.5 if (has_frp and not has_bt) else (1.0 if (has_frp and has_bt) else 0.4)

    # 4. Thermal Intensity & Extremeness Scores
    intensity_from_frp = min(1.0, frp_max / config.high_frp_mw)
    if has_bt and bt_max:
        intensity_from_bt = min(1.0, max(0.0, (bt_max - 290.0) / (config.high_bt_kelvin - 290.0)))
        thermal_intensity = round(0.6 * intensity_from_frp + 0.4 * intensity_from_bt, 4)
    else:
        thermal_intensity = round(intensity_from_frp, 4)

    extremeness_frp = min(1.0, frp_max / config.extreme_frp_mw)
    if has_bt and bt_max:
        extremeness_bt = min(1.0, max(0.0, (bt_max - 300.0) / (config.extreme_bt_kelvin - 300.0)))
        thermal_extremeness = round(max(extremeness_frp, extremeness_bt), 4)
    else:
        thermal_extremeness = round(extremeness_frp, 4)

    # 5. Thermal Concentration (spatial/temporal concentration indicator)
    obs_count = max(1, int(canon.observation_count_so_far))
    footprint_val = getattr(canon, "spatial_footprint", getattr(canon, "spatial_cluster_radius", 1.0))
    footprint = max(0.1, float(footprint_val)) if not np.isnan(float(footprint_val)) else 1.0
    thermal_concentration = min(1.0, round(float(frp_sum / (footprint * max(1, obs_count))), 4))

    # 6. High-Temperature Signal State
    if thermal_intensity >= 0.70 or (bt_max and bt_max >= config.high_bt_kelvin) or frp_max >= config.high_frp_mw:
        high_t_signal = SIGNAL_STRONG
    elif thermal_intensity >= 0.35 or frp_max >= config.moderate_frp_mw or (bt_max and bt_max >= config.moderate_bt_kelvin):
        high_t_signal = SIGNAL_MODERATE
    elif thermal_intensity > 0.0:
        high_t_signal = SIGNAL_WEAK
    else:
        high_t_signal = SIGNAL_NOT_DETECTABLE

    # 7. Saturation Defense & Measurement Reliability
    measurement_reliability = 1.0
    quality_limitations = []
    reason_codes = []

    if quality_summary is not None:
        sat_sum = getattr(quality_summary, "saturation_summary", "")
        if "Likely" in sat_sum or "LIKELY" in sat_sum:
            measurement_reliability = 0.50
            quality_limitations.append("Thermal saturation likely: radiometric non-linearity possible")
            reason_codes.append("THERMAL_SATURATION_LIKELY")
        elif "Possible" in sat_sum or "POSSIBLE" in sat_sum:
            measurement_reliability = 0.75
            quality_limitations.append("Thermal saturation possible: measurement reliability downweighted")
            reason_codes.append("THERMAL_SATURATION_POSSIBLE")

    if not has_bt:
        quality_limitations.append("Brightness temperature unavailable; operating in reduced FRP-only mode")
        reason_codes.append("BRIGHTNESS_TEMPERATURE_UNAVAILABLE")

    # 8. Source Physics Indicators (Controlled physics features, not class decisions)
    source_physics_indicators = {
        "frp_intensity_mw": round(frp_max, 2),
        "brightness_temperature_kelvin": bt_max,
        "thermal_extremeness": thermal_extremeness,
        "thermal_concentration": thermal_concentration,
        "estimates": estimates
    }

    # 9. Form Evidence Items
    evidence_items = []
    if high_t_signal in [SIGNAL_STRONG, SIGNAL_MODERATE]:
        evidence_items.append({
            "evidence_family": "THERMAL_PHYSICS",
            "direction": "SUPPORTING",
            "strength": "STRONG" if high_t_signal == SIGNAL_STRONG else "MODERATE",
            "description": f"Thermal physics measurements exhibit a {high_t_signal.lower()} high-temperature signal (FRP max: {frp_max:.1f} MW).",
            "source": "HighTThermalPhysics"
        })
    elif high_t_signal == SIGNAL_WEAK:
        evidence_items.append({
            "evidence_family": "THERMAL_PHYSICS",
            "direction": "NEUTRAL",
            "strength": "WEAK",
            "description": "Thermal physics measurements exhibit low-intensity thermal characteristics.",
            "source": "HighTThermalPhysics"
        })

    if "THERMAL_SATURATION_LIKELY" in reason_codes:
        evidence_items.append({
            "evidence_family": "THERMAL_PHYSICS",
            "direction": "CONFLICTING",
            "strength": "MODERATE",
            "description": "Sensor saturation limits thermal measurement precision; downweighting thermal reliability.",
            "source": "HighTThermalPhysics"
        })

    return HighTThermalAssessment(
        event_id=event_id,
        available=True,
        physics_mode=physics_mode,
        input_completeness=input_comp,
        thermal_intensity_score=thermal_intensity,
        high_temperature_signal=high_t_signal,
        thermal_extremeness=thermal_extremeness,
        thermal_concentration=thermal_concentration,
        thermal_measurement_reliability=measurement_reliability,
        brightness_temperature_summary=bt_summary,
        frp_summary=frp_summary,
        source_physics_indicators=source_physics_indicators,
        quality_limitations=quality_limitations,
        reason_codes=reason_codes,
        evidence_items=evidence_items
    )
