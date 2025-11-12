from pydantic import BaseModel
from typing import List, Optional

class EV(BaseModel):
    id: str
    battery: int  # percentage 0-100
    lat: float
    lon: float
    assigned_station: Optional[str] = None

class Station(BaseModel):
    id: str
    lat: float
    lon: float
    capacity: int  # number of chargers
    occupied: int = 0

class FleetData(BaseModel):
    evs: List[EV]
    stations: List[Station]
