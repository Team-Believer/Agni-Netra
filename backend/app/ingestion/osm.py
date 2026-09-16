from typing import Dict, Any, Optional
import math

class OsmFacilityAdapter:
    """
    Adapter for OpenStreetMap and GIDC industrial zones, petrochemical refineries,
    power plants, and critical infrastructure.
    """
    def __init__(self):
        self.known_facilities = [
            {
                "name": "Reliance Jamnagar Refinery Complex",
                "type": "Petrochemical Refinery",
                "lat": 22.4707,
                "lon": 70.0577,
                "district": "Jamnagar",
                "state": "Gujarat",
                "radius_km": 6.5,
                "criticality": "CRITICAL_NATIONAL_INFRASTRUCTURE"
            },
            {
                "name": "IOCL Mathura Refinery",
                "type": "Petroleum Refinery",
                "lat": 27.4924,
                "lon": 77.6737,
                "district": "Mathura",
                "state": "Uttar Pradesh",
                "radius_km": 3.0,
                "criticality": "HIGH_STRATEGIC"
            },
            {
                "name": "Paradip Petrochemicals & Port Zone",
                "type": "Port & Chemical Hub",
                "lat": 20.3165,
                "lon": 86.6115,
                "district": "Paradip",
                "state": "Odisha",
                "radius_km": 4.5,
                "criticality": "HIGH_STRATEGIC"
            },
            {
                "name": "Bhilai Steel Plant",
                "type": "Metallurgical Plant",
                "lat": 21.1895,
                "lon": 81.3855,
                "district": "Durg",
                "state": "Chhattisgarh",
                "radius_km": 5.0,
                "criticality": "HIGH"
            }
        ]

    def find_nearest_facility(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        best_fac = None
        min_dist_km = float("inf")

        for fac in self.known_facilities:
            # Haversine distance
            dlat = math.radians(fac["lat"] - lat)
            dlon = math.radians(fac["lon"] - lon)
            a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(fac["lat"])) * math.sin(dlon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            dist_km = 6371.0 * c

            if dist_km < min_dist_km:
                min_dist_km = dist_km
                best_fac = {**fac, "distance_km": round(dist_km, 2)}

        return best_fac
