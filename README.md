GreenMove – EV Fleet Charging Optimization

A smart optimization system that assigns electric vehicles (EVs) in a fleet to the best charging stations, minimizing travel distance, waiting time, and load imbalance. Inspired by Google Maps’ eco-routing and logistics optimization.

This project demonstrates IoT + optimization + cloud + visualization, showing how software can make EV fleets more efficient and sustainable.

🚀 Features

Assigns EVs to charging stations using optimization algorithms.

Considers:

Vehicle battery %

Distance to stations

Station availability (charging slots)

Real-time map visualization of EVs, charging stations, and assignments.

REST API to run optimization and fetch fleet status.

Lightweight, scalable, and deployable with free-tier resources.

🛠️ Tech Stack
Backend

FastAPI
 → REST API + WebSocket support

Python OR-Tools
 → optimization algorithms (assignment & routing)

PostgreSQL
 → store EV + station data (free via Supabase/Neon)

Paho-MQTT / asyncio-mqtt
 → optional IoT data integration (simulated EV telemetry)

Frontend

React
 + TypeScript
 + Vite
 → modern, fast frontend

Leaflet.js
 → interactive maps for EVs + stations

Recharts
 → battery % and utilization charts

Tailwind CSS
 → clean, responsive UI

Deployment (Free Tiers)

Backend → Railway
 / Render

Frontend → Vercel
 / Netlify

Database → Supabase
 / Neon

IoT Broker → Eclipse Mosquitto
 (public MQTT broker)

📦 Project Structure
ev-fleet-charging-optimization/
│── backend/            # FastAPI + optimization logic
│   ├── main.py         # API endpoints
│   ├── optimizer.py    # OR-Tools / assignment logic
│   ├── models.py       # DB models (SQLAlchemy)
│── frontend/           # React + TS + Vite app
│   ├── src/
│   │   ├── App.tsx     # Main dashboard
│   │   ├── Map.tsx     # Leaflet map
│   │   ├── api.ts      # Backend API calls
│── iot-simulator/      # Python script simulating EV telemetry
│   ├── simulator.py
│── README.md           # Project documentation

⚡ Quick Start
1️⃣ Backend (FastAPI)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload


API endpoints:

POST /assign-charging → run optimization

GET /fleet-status → get EV + station info

2️⃣ Frontend (React + Vite + TS)
cd frontend
npm install
npm run dev

3️⃣ IoT Simulation (Optional)
cd iot-simulator
python simulator.py

🌍 Demo Flow

Open dashboard → see EVs + charging stations on map.

Click “Run Optimization”.

Backend assigns EVs → charging stations.

Map updates with arrows showing assignments.

📊 Example Output

EV1 (30% battery) → Station A (2 km away).

EV2 (20% battery) → Station B (closer, free slot).

EV3 (60% battery) → stays idle (no charging needed).
