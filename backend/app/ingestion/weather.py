from typing import Dict, Any, Optional
import datetime

class WeatherAdapter:
    """
    Adapter for IMD / ECMWF atmospheric weather conditions:
    Wind speed, wind direction, ambient surface temperature, relative humidity.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.source_name = "IMD_WEATHER"

    def get_conditions(self, lat: float, lon: float, timestamp: datetime.datetime) -> Optional[Dict[str, Any]]:
        # No actual weather API configured
        return None

    def get_status(self) -> Dict[str, Any]:
        return {
            "source": self.source_name,
            "status": "NOT CONFIGURED",
            "coverage": "Global"
        }
