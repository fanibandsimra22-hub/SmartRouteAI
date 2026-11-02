# SmartRoute AI – AI-Powered Real-World City Navigation System

SmartRoute AI is an engineering B.Tech project implementing an intelligent urban navigation and graph pathfinding engine for real-world road networks in Goa, India.

The project integrates a **React 19 + Leaflet** interactive frontend, a **Python FastAPI** backend engine, **NetworkX 3.7 & OSMnx 2.1.1** for graph analysis, **OpenStreetMap** road networks and geocoding, and **MongoDB Atlas** for route bookmarking and history.

---

## 🌟 Key Features

### 1. Real-World Road Network Navigation
- Ingests and processes genuine OpenStreetMap (OSM) driving network data for the **Central Goa Urban & Zuari Highway Corridor** spanning **Panaji, Miramar, Dona Paula, Taleigao, Bambolim, Goa University, Cortalim, Zuari Bridge, and Verna (PCCE)**.
- Active road network graph: **6,407 nodes, 15,455 edges, and 1,947.8 km of drivable roads**.
- Reconstructs actual road-edge curved geometry (Shapely `LineString`) and renders accurate polylines on the map.
- Generates human-friendly **turn-by-turn instructions** with compass bearings, turn angles, and official street names.
- Computes actual road distance (km), estimated travel times (minutes), average vehicle speeds, and estimated fuel consumption ($0.08\text{ L/km}$).

### 2. Multi-Objective AI Pathfinding Algorithms
- **A\* Search (Default Navigation Algorithm):**
  - **Fastest-Time Routing:** Optimizes for travel time using road speed limits and edge travel times.
  - **Shortest-Distance Routing:** Optimizes for physical road distance using edge lengths.
  - **Admissible Lower-Bound Heuristics:** Employs a conservative graph-wide distance scaling factor ($\alpha$) and dynamic maximum effective speed derivation ($V_{\max\_effective}$), mathematically guaranteeing optimal, admissible path finding without overestimation.
- **Dijkstra's Algorithm (Benchmark Standard):**
  - Evaluates true optimal graph cost without heuristics.
  - Mathematically verified to return identical optimal costs as A\*.
- **BFS & DFS (Academic Demonstrations):**
  - Available via API parameters for academic comparison of unweighted path length and exploration behavior.

### 3. Automatic Geolocation & Interactive Map Dashboard
- **Automatic Current Location Detection:**
  - On application startup, requests user permission via the browser Geolocation API.
  - If granted, automatically sets the user's real GPS position as the starting point ("My Current Location"), displays a pulsing beacon on the map, and computes navigation to the destination.
  - Gracefully falls back to Panaji if permission is denied, with a friendly dismissable notice banner.
- **Smart Destination Search & Autocomplete:**
  - Comprehensive alias matching for educational institutions and landmarks (e.g., searching `"PCCE"` or `"Padre Conceicao"` instantly returns Padre Conceicao College of Engineering at Agnel Ashram, Verna: `15.3562 N, 73.9317 E`).
  - Includes BITS Pilani Goa Campus, GEC Farmagudi, DBCE Fatorda, NIT Goa, GMC Bambolim, and Goa University.
- **Interactive Location Selection:**
  - Map-click selection mode: Pick origin or destination points directly on the interactive map canvas.
  - Draggable pins: Drag green Origin marker (A) or red Destination marker (B) to recalculate routes dynamically.
  - Strict boundary validation ($> 3.5\text{ km}$ snapping threshold) prevents misleading routes for locations outside corridor coverage.
- **Side-by-Side Route Comparison:** Switch between Fastest Route (⚡ Speed Priority) and Shortest Route (📏 Distance Priority) with instant polyline updates.

### 4. Database Persistence (MongoDB Atlas)
- **Saved Routes:** Bookmark favorite routes with one-click reload into the map and planner.
- **Route History:** Automatically logs navigation queries with timestamps, execution metrics, and traffic conditions.
- **Resilient Fallback:** Seamless in-memory adapter ensures uninterrupted demonstration even if the remote Atlas cluster is temporarily unreachable.

### 5. Transparent Traffic Status
- Supports real-time traffic via **TomTom Traffic Flow API** when `TOMTOM_API_KEY` is configured in `backend/.env`.
- If TomTom credentials are absent, the system transparently indicates **BASELINE** speeds derived from OpenStreetMap speed tags.
- Adheres strictly to scientific honesty: never fabricates simulated "live" traffic.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 19, Vite 8, Tailwind CSS v4, Leaflet.js 1.9, React-Leaflet 5, Lucide React, Oxlint |
| **Backend API** | Python 3.10+, FastAPI 0.115, Uvicorn, Pydantic v2, Pydantic-Settings |
| **Graph & AI Engine** | NetworkX 3.7, OSMnx 2.1.1, Shapely, NumPy |
| **Geocoding & Maps** | OpenStreetMap Nominatim, Leaflet TileLayer (OSM Standard & CARTO Voyager) |
| **Traffic Integration** | TomTom Traffic API (optional) with OpenStreetMap baseline fallback |
| **Database** | MongoDB Atlas, PyMongo 4.9, dnspython |

---

## 📁 Project Folder Structure

```
SmartRouteAI/
├── backend/
│   ├── app/
│   │   ├── algorithms/          # Pathfinding implementations
│   │   │   ├── astar.py         # A* algorithm with admissible heuristic
│   │   │   ├── dijkstra.py      # Dijkstra benchmark algorithm
│   │   │   ├── bfs.py           # Breadth-First Search
│   │   │   ├── dfs.py           # Depth-First Search
│   │   │   └── common.py        # Haversine, scaling factor alpha, edge resolution
│   │   ├── models/              # MongoDB document models
│   │   ├── routes/              # FastAPI endpoint routers
│   │   │   ├── health.py        # GET /api/health
│   │   │   ├── locations.py     # GET /api/locations/search
│   │   │   ├── routing.py       # POST /api/calculate-route
│   │   │   └── routes_history.py# GET/POST/DELETE /api/routes/*
│   │   ├── schemas/             # Pydantic request & response validation
│   │   ├── services/            # Core business logic
│   │   │   ├── geocoding_service.py # Nominatim + curated landmarks
│   │   │   ├── graph_service.py     # OSMnx graph caching & spatial indexing
│   │   │   ├── routing_service.py   # Route geometry & turn-by-turn synthesis
│   │   │   └── traffic_service.py   # TomTom live traffic & baseline fallback
│   │   ├── config.py            # Pydantic BaseSettings loading from .env
│   │   ├── database.py          # MongoDB Atlas connection manager & in-memory fallback
│   │   └── main.py              # FastAPI application entry point
│   ├── data/
│   │   └── cache/               # Cached GraphML road networks
│   │       ├── goa_central_roads.graphml     # Genuine 6,407-node OSM network (Panaji - PCCE Verna)
│   │       └── goa_prototype_corridor.graphml# 23-node benchmark corridor
│   ├── tests/                   # Automated test suites
│   │   ├── test_algorithms.py   # Unit & optimality tests for A*, Dijkstra, BFS, DFS
│   │   ├── test_api_endpoints.py# Full API integration test suite
│   │   ├── test_database.py     # MongoDB operations & connectivity tests
│   │   ├── test_graph_service.py# Graph loading & nearest-node tests
│   │   └── test_health.py       # System health check tests
│   ├── .env                     # Local environment secrets (not committed)
│   ├── .env.example             # Configuration template
│   ├── requirements.txt         # Python package dependencies
│   └── run_backend.py           # Single-command backend server launcher
├── src/                         # React frontend source code
│   ├── components/              # UI components
│   │   ├── Header.jsx           # App bar & architecture modal
│   │   ├── LocationAutocompleteInput.jsx # Live Nominatim & landmark search
│   │   ├── MapControls.jsx      # Zoom, recenter, reset Goa view, tile switches
│   │   ├── MapPlaceholder.jsx   # Leaflet map canvas with draggable markers & GPS dot
│   │   ├── RouteCard.jsx        # Fastest vs Shortest selection cards
│   │   ├── RouteResults.jsx     # Route metrics, turn-by-turn directions, bookmarking
│   │   ├── RouteSearchForm.jsx  # Origin/dest inputs, GPS button, map-pick toggles
│   │   ├── SavedRoutesModal.jsx # MongoDB saved routes & search history drawer
│   │   └── TrafficPanel.jsx     # Traffic condition status panel
│   ├── data/                    # Landmark coordinates & presets
│   ├── services/                # API client services
│   │   ├── locationService.js   # Geocoding API client
│   │   └── routeService.js      # Route calculation & MongoDB API client
│   ├── utils/                   # GeoUtils & Haversine distance functions
│   ├── App.jsx                  # Main application orchestrator
│   └── main.jsx                 # React root entry point
├── package.json                 # Node.js dependencies & scripts
├── vite.config.js               # Vite bundler configuration
└── README.md                    # Project documentation
```

---

## ⚡ Installation & Setup Instructions

### Prerequisites
- **Node.js** (v18 or higher) & **npm**
- **Python** (v3.10 or higher)
- **Windows PowerShell** (or Linux/macOS bash)

---

### Step 1: Backend Setup

1. Open PowerShell and navigate to the project directory:
   ```powershell
   cd C:\Users\LENOVO\SmartRouteAI
   ```

2. Create and activate a Python virtual environment:
   ```powershell
   python -m venv backend\venv
   .\backend\venv\Scripts\Activate.ps1
   ```

3. Install required Python packages:
   ```powershell
   pip install -r backend\requirements.txt
   ```

4. Verify environment configuration:
   Ensure `backend/.env` contains your MongoDB Atlas connection string:
   ```ini
   MONGODB_URI="mongodb+srv://<username>:<password>@cluster0.mongodb.net/smartroute_ai?retryWrites=true&w=majority"
   MONGODB_DB_NAME="smartroute_ai"
   TOMTOM_API_KEY="" # Optional
   ```

---

### Step 2: Frontend Setup

1. In the project root, install Node dependencies:
   ```powershell
   npm install
   ```

2. Verify code quality with the linter:
   ```powershell
   npm run lint
   ```

3. Verify production bundling:
   ```powershell
   npm run build
   ```

---

## 🚀 Running the Project for Demonstration

### Option A: Start the Backend Server
Run the backend server using the dedicated launcher:
```powershell
.\backend\venv\Scripts\python.exe backend\run_backend.py
```
- **Backend API URL:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check:** [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### Option B: Start the Frontend Application
In a separate terminal window, launch the Vite development server:
```powershell
npm run dev
```
- **Web Application URL:** [http://localhost:5173](http://localhost:5173)

---

## 📡 Key Tested Route Pairs

| Route Query | Origin -> Destination | Distance | Time | Verified Status |
| :--- | :--- | :--- | :--- | :--- |
| **Urban Short** | Panaji Church -> Miramar Beach | 2.92 km | ~4 mins | Verified (56 coords, 10 instructions) |
| **Scenic Coast** | Panaji Church -> Dona Paula | 6.37 km | ~8 mins | Verified (153 coords, 16 instructions) |
| **Campus Drive** | Panaji Church -> Goa University | 6.44 km | ~8 mins | Verified (174 coords, 14 instructions) |
| **College Corridor** | PCCE Verna -> Panaji Church | 23.16 km | ~27 mins | Verified (575 coords, 31 instructions) |
| **Regional Highway**| Bambolim -> PCCE Verna | 17.65 km | ~18 mins | Verified (401 coords, 12 instructions) |
| **Out-of-Bounds** | Mumbai -> Panaji | N/A | N/A | Correctly rejected (> 3.5 km boundary check) |

---

## 🧮 Algorithm & Heuristic Admissibility

### 1. Distance Scaling Factor ($\alpha$)
Because road networks can occasionally include simplified geometries where straight-line Haversine distance between adjacent intersection nodes slightly exceeds the recorded edge length, a naive Haversine heuristic may overestimate remaining distance ($h(u) > h^*(u)$), violating A\* admissibility.

SmartRoute AI computes a conservative graph-wide distance scaling factor:
$$\alpha = \min\left(1.0, \min_{e \in E} \frac{\text{length}(e)}{\text{Haversine}(u, v)}\right)$$
- On the Central Goa road network, $\alpha \approx 0.7466$.
- Safely excludes zero-displacement nodes and point vertices.

### 2. A\* Shortest-Distance Heuristic
$$h_{\text{dist}}(u, t) = \alpha \times \text{Haversine}(u, t)$$
- **Guarantee:** Never exceeds actual road network distance. Provably admissible and monotonic.

### 3. A\* Fastest-Time Heuristic
$$h_{\text{time}}(u, t) = \frac{\alpha \times \text{Haversine}(u, t)}{V_{\max\_effective}}$$
- $V_{\max\_effective}$ is derived dynamically across all graph edges:
  $$V_{\max\_effective} = \max_{e \in E} \left(\frac{\text{length}(e)}{\text{travel\_time}(e)}, \frac{\text{speed\_kph}(e) \times 1000}{3600}\right)$$
- **Guarantee:** Never underestimates remaining travel time. Mathematically optimal.

---

## 🧪 Automated Test Suites

The project includes 5 comprehensive test suites covering all layers. Run them using the backend virtual environment:

```powershell
# 1. Pathfinding Algorithms (12 test cases)
.\backend\venv\Scripts\python.exe backend\tests\test_algorithms.py

# 2. Full API Endpoints (10 integration tests)
.\backend\venv\Scripts\python.exe backend\tests\test_api_endpoints.py

# 3. Graph Service & Nearest-Node Spatial Lookup (5 tests)
.\backend\venv\Scripts\python.exe backend\tests\test_graph_service.py

# 4. MongoDB Atlas Database Operations (6 tests)
.\backend\venv\Scripts\python.exe backend\tests\test_database.py

# 5. API Health & Diagnostic Endpoint (2 tests)
.\backend\venv\Scripts\python.exe backend\tests\test_health.py

# 6. Frontend Linter & Production Build
npm run lint
npm run build
```

---

## ⚠️ Known Boundaries & Scope

1. **Geographical Coverage Corridor:**
   The active OpenStreetMap graph covers the **Central Goa Urban Corridor** spanning from Panaji southwards across the Zuari Bridge down to Verna (PCCE), encompassing 6,407 nodes and 15,455 edges. Coordinates outside this boundary are rejected with a clear message to prevent inaccurate snapping.
2. **Traffic Integration:**
   Live traffic flow updates are queried via TomTom when an API key is provided; otherwise, baseline OSM legal speed limits are used with a transparent "BASELINE" status indicator.
3. **Session Authentication:**
   The current demonstration operates as a guest session for rapid college evaluation.
