from typing import Dict, Any, Optional
import datetime

class WeatherAdapter:
    """
    Adapter for IMD / ECMWF atmospheric weather conditions:
    Wind speed, wind direction, ambient surface temperature, relative humidity.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.source_name = "IMD_WEATHER"

    def get_conditions(self, lat: float, lon: float, timestamp: datetime.datetime) -> Dict[str, Any]:
        return {
            "source": self.source_name,
            "wind_speed_kmh": 18.5,
            "wind_direction_deg": 245.0, # WSW
            "ambient_temp_c": 33.2,
            "humidity_pct": 42.0,
            "boundary_layer_height_m": 850.0,
            "atmospheric_stability": "UNSTABLE_CONVECTIVE"
        }
