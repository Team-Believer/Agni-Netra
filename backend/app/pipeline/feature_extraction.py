from typing import List, Dict, Any
import numpy as np
import datetime
import math

def extract_canonical_features(observations: List[Dict[str, Any]], history_window_days: float = 30.0) -> Dict[str, Any]:
    """
    Extracts the 24 canonical features expected by the trained XGBoost model (xgboost_b0.json)
    defined in models/b0/model_config.json.
    """
    if not observations:
        return {}

    # Sort chronologically
    sorted_obs = sorted(observations, key=lambda x: x["timestamp"])
    frps = [float(obs.get("frp", 10.0) or 10.0) for obs in sorted_obs]
    bts = [float(obs.get("brightness_temperature", 310.0) or 310.0) for obs in sorted_obs]
    confs = [float(obs.get("confidence", 0.8) or 0.8) for obs in sorted_obs]
    
    t_first = sorted_obs[0]["timestamp"]
    t_last = sorted_obs[-1]["timestamp"]
    if isinstance(t_first, str):
        t_first = datetime.datetime.fromisoformat(t_first.replace("Z", "+00:00"))
    if isinstance(t_last, str):
        t_last = datetime.datetime.fromisoformat(t_last.replace("Z", "+00:00"))

    duration_hours = max(0.1, (t_last - t_first).total_seconds() / 3600.0)
    obs_count = len(sorted_obs)
    obs_per_day = obs_count / max(0.1, duration_hours / 24.0)

    # Intervals / gaps
    gaps = []
    for i in range(1, len(sorted_obs)):
        t1 = sorted_obs[i-1]["timestamp"]
        t2 = sorted_obs[i]["timestamp"]
        if isinstance(t1, str):
            t1 = datetime.datetime.fromisoformat(t1.replace("Z", "+00:00"))
        if isinstance(t2, str):
            t2 = datetime.datetime.fromisoformat(t2.replace("Z", "+00:00"))
        gaps.append(max(0.0, (t2 - t1).total_seconds() / 3600.0))
    
    median_gap = float(np.median(gaps)) if gaps else 0.0
    max_gap = float(np.max(gaps)) if gaps else 0.0

    # Day/Night ratio
    day_count = sum(1 for obs in sorted_obs if 6 <= (obs["timestamp"].hour if hasattr(obs["timestamp"], "hour") else 12) <= 18)
    night_count = obs_count - day_count
    day_night_ratio = float(day_count / max(1, night_count))

    # Spatial spread
    lats = [obs["latitude"] for obs in sorted_obs]
    lons = [obs["longitude"] for obs in sorted_obs]
    dlat = (max(lats) - min(lats)) * 111.0
    dlon = (max(lons) - min(lons)) * 111.0 * math.cos(math.radians(sum(lats) / len(lats)))
    spatial_spread_km = float(math.sqrt(dlat**2 + dlon**2))

    # Satellites
    sats = set(obs.get("satellite_sensor", "VIIRS") for obs in sorted_obs)
    num_satellites = len(sats)

    mean_frp = float(np.mean(frps))
    max_frp = float(np.max(frps))
    min_frp = float(np.min(frps))
    frp_std = float(np.std(frps)) if len(frps) > 1 else 0.0
    frp_cv = float(frp_std / max(0.1, mean_frp))
    frp_first = float(frps[0])
    frp_last = float(frps[-1])
    frp_change = float(frp_last - frp_first)

    expanding_indicator = 1.0 if (spatial_spread_km > 1.0 and frp_change > 0) else 0.0
    stable_indicator = 1.0 if (frp_cv < 0.25 and spatial_spread_km < 0.5) else 0.0
    sudden_frp_increase = 1.0 if (frp_last > 2.0 * max(1.0, mean_frp) and frp_change > 20.0) else 0.0

    return {
        "mean_frp": mean_frp,
        "max_frp": max_frp,
        "min_frp": min_frp,
        "frp_std": frp_std,
        "frp_cv": frp_cv,
        "frp_first": frp_first,
        "frp_last": frp_last,
        "frp_change": frp_change,
        "brightness_mean": float(np.mean(bts)),
        "brightness_max": float(np.max(bts)),
        "duration_hours": duration_hours,
        "observation_count": obs_count,
        "obs_per_day": obs_per_day,
        "median_gap": median_gap,
        "max_gap": max_gap,
        "day_night_ratio": day_night_ratio,
        "spatial_spread_km": spatial_spread_km,
        "num_satellites": num_satellites,
        "expanding_indicator": expanding_indicator,
        "stable_indicator": stable_indicator,
        "sudden_frp_increase": sudden_frp_increase,
        "min_confidence": float(np.min(confs)),
        "mean_confidence": float(np.mean(confs)),
        "history_window_days": float(history_window_days)
    }
