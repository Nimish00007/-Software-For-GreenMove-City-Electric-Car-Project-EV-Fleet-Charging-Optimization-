import requests
import math
import os
from typing import List, Dict
from models import EV, Station

# OSRM public router (no key required). If that fails, optional OpenRouteService is used if you set ORS_API_KEY.
OSRM_URL = "https://router.project-osrm.org/route/v1/driving"
ORS_API_KEY = os.getenv("ORS_API_KEY")
ORS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"

def real_distance(ev: EV, station: Station) -> float:
    """
    Return driving distance in meters between ev and station.
    Strategy:
      1) Try OSRM public server.
      2) If that fails and ORS_API_KEY env var exists, try OpenRouteService.
      3) Fallback to an approximate Euclidean->meters conversion.
    """
    try:
        coords = f"{ev.lon},{ev.lat};{station.lon},{station.lat}"
        url = f"{OSRM_URL}/{coords}?overview=false"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        return data["routes"][0]["distance"]  # meters
    except Exception:
        # try ORS if key is present
        if ORS_API_KEY:
            try:
                params = {
                    "api_key": ORS_API_KEY,
                    "start": f"{ev.lon},{ev.lat}",
                    "end": f"{station.lon},{station.lat}"
                }
                r = requests.get(ORS_URL, params=params, timeout=5)
                r.raise_for_status()
                data = r.json()
                return data["features"][0]["properties"]["segments"][0]["distance"]
            except Exception:
                pass
    # Fallback: approximate lat/lon degrees to meters
    lat_diff_m = (ev.lat - station.lat) * 111320  # approx meters per deg latitude
    lon_diff_m = (ev.lon - station.lon) * 111320 * math.cos(math.radians(ev.lat))
    return math.sqrt(lat_diff_m**2 + lon_diff_m**2)

def assign_charging(evs: List[EV], stations: List[Station]) -> List[Dict]:
    """
    Simple greedy assignment:
      - sort EVs by battery ascending (low battery first)
      - for each EV pick nearest station that has capacity left
    Returns list of assignments with distances.
    """
    assignments = []

    # Reset station occupied if not present
    for s in stations:
        if not hasattr(s, "occupied"):
            s.occupied = 0

    evs_sorted = sorted(evs, key=lambda e: e.battery)

    for ev in evs_sorted:
        best_station = None
        best_dist = float("inf")
        for station in stations:
            if station.occupied < station.capacity:
                d = real_distance(ev, station)
                if d < best_dist:
                    best_dist = d
                    best_station = station

        if best_station:
            ev.assigned_station = best_station.id
            best_station.occupied += 1
            assignments.append({
                "ev": ev.id,
                "station": best_station.id,
                "distance_m": round(best_dist, 2)
            })
    return assignments
