from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from models import FleetData, EV, Station
from optimizer import assign_charging, real_distance
from apscheduler.schedulers.background import BackgroundScheduler
import random
import asyncio
import json
from typing import List

app = FastAPI(title="GreenMove - EV Fleet Charging Optimizer (Backend)")

# ---------------------------
# Sample in-memory fleet data
# ---------------------------
fleet_data = FleetData(
    evs=[
        EV(id="UNO", battery=30, lat=40.7128, lon=-74.0060),
        EV(id="DUO-Y", battery=20, lat=40.7138, lon=-74.0050),
        EV(id="LIVRO", battery=60, lat=40.7150, lon=-74.0070),
        EV(id="DUO-S", battery=80, lat=40.7165, lon=-74.0085),
        EV(id="UNO-2", battery=50, lat=40.7145, lon=-74.0040),
    ],
    stations=[
        Station(id="Station-A", lat=40.7200, lon=-74.0100, capacity=2),
        Station(id="Station-B", lat=40.7300, lon=-74.0000, capacity=1),
        Station(id="Station-C", lat=40.7400, lon=-74.0020, capacity=2),
    ]
)

# ---------------------------
# EV movement simulator
# ---------------------------
def simulate_ev_movement():
    """
    Called periodically by scheduler.
    Random small shifts in latitude/longitude simulate driving.
    Battery drains slowly.
    """
    for ev in fleet_data.evs:
        ev.lat += random.uniform(-0.0005, 0.0005)
        ev.lon += random.uniform(-0.0005, 0.0005)
        ev.battery = max(0, ev.battery - random.randint(0, 2))

        # simple rule: if battery hits 0, "reset" to 100 (simulate charging)
        if ev.battery == 0:
            ev.battery = 100
            ev.assigned_station = None

# ---------------------------
# WebSocket connection manager
# ---------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        # send to all active connections
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception:
                # if send fails, remove connection
                try:
                    self.active_connections.remove(connection)
                except ValueError:
                    pass

manager = ConnectionManager()

# ---------------------------
# Scheduler: update & broadcast
# ---------------------------
async def broadcast_fleet():
    payload = {
        "evs": [ev.dict() for ev in fleet_data.evs],
        "stations": [s.dict() for s in fleet_data.stations]
    }
    await manager.broadcast(json.dumps(payload))

def scheduled_job():
    simulate_ev_movement()
    # schedule the broadcast on the event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    asyncio.run_coroutine_threadsafe(broadcast_fleet(), loop)

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_job, "interval", seconds=5)  # update every 5s
scheduler.start()

# ---------------------------
# REST endpoints
# ---------------------------
@app.get("/fleet-status")
async def get_fleet_status():
    """
    Returns current EVs and stations (positions, battery, assigned station, occupancy).
    """
    return fleet_data

@app.post("/assign-charging")
async def assign_charging_endpoint():
    """
    Run optimization and return assignments.
    """
    # Reset occupied counts before assignment
    for s in fleet_data.stations:
        s.occupied = 0
    assignments = assign_charging(fleet_data.evs, fleet_data.stations)
    return {"assignments": assignments}

@app.get("/nearby-stations/{ev_id}")
async def get_nearby_stations(ev_id: str):
    """
    Returns stations sorted by driving distance for the given EV id.
    """
    ev = next((e for e in fleet_data.evs if e.id == ev_id), None)
    if not ev:
        return {"error": "EV not found"}
    stations_sorted = sorted(fleet_data.stations, key=lambda s: real_distance(ev, s))
    return {
        "ev": ev.id,
        "battery": ev.battery,
        "nearby_stations": [
            {"station": s.id, "distance_m": round(real_distance(ev, s), 2)}
            for s in stations_sorted
        ]
    }

# ---------------------------
# WebSocket endpoint for real-time updates
# ---------------------------
@app.websocket("/ws/fleet")
async def websocket_endpoint(websocket: WebSocket):
    """
    Clients (frontend) can open a websocket to /ws/fleet to receive periodic fleet updates (every 5s).
    """
    await manager.connect(websocket)
    try:
        while True:
            # keep connection open; server pushes updates via broadcast_fleet() scheduled job
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
