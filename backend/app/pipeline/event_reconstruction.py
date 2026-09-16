from typing import List, Dict, Any
import datetime
import math
import json

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class EventReconstructor:
    """
    Reconstructs continuous physical thermal events from individual multi-sensor observations.
    Clusters observations within spatial radius (e.g. 3.0 km) and temporal window (e.g. 24 hours).
    """
    def __init__(self, spatial_threshold_km: float = 3.0, temporal_threshold_hours: float = 24.0):
        self.spatial_threshold_km = spatial_threshold_km
        self.temporal_threshold_hours = temporal_threshold_hours

    def cluster_observations(self, observations: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        if not observations:
            return []

        # Sort by timestamp
        sorted_obs = sorted(observations, key=lambda x: x["timestamp"])
        clusters: List[List[Dict[str, Any]]] = []

        for obs in sorted_obs:
            assigned = False
            obs_time = obs["timestamp"]
            if isinstance(obs_time, str):
                obs_time = datetime.datetime.fromisoformat(obs_time.replace("Z", "+00:00"))

            for cluster in clusters:
                last_obs = cluster[-1]
                last_time = last_obs["timestamp"]
                if isinstance(last_time, str):
                    last_time = datetime.datetime.fromisoformat(last_time.replace("Z", "+00:00"))

                time_diff_hours = abs((obs_time - last_time).total_seconds()) / 3600.0
                if time_diff_hours <= self.temporal_threshold_hours:
                    # Check spatial distance to cluster centroid
                    cent_lat = sum(o["latitude"] for o in cluster) / len(cluster)
                    cent_lon = sum(o["longitude"] for o in cluster) / len(cluster)
                    dist_km = calculate_haversine_distance(obs["latitude"], obs["longitude"], cent_lat, cent_lon)
                    if dist_km <= self.spatial_threshold_km:
                        cluster.append(obs)
                        assigned = True
                        break

            if not assigned:
                clusters.append([obs])

        return clusters

    def create_bounding_geojson(self, cluster: List[Dict[str, Any]]) -> str:
        lats = [o["latitude"] for o in cluster]
        lons = [o["longitude"] for o in cluster]
        min_lat, max_lat = min(lats) - 0.005, max(lats) + 0.005
        min_lon, max_lon = min(lons) - 0.005, max(lons) + 0.005
        
        polygon = {
            "type": "Polygon",
            "coordinates": [[
                [min_lon, min_lat],
                [max_lon, min_lat],
                [max_lon, max_lat],
                [min_lon, max_lat],
                [min_lon, min_lat]
            ]]
        }
        return json.dumps(polygon)
