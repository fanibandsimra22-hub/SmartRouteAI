/**
 * routeService.js
 * 
 * Route Computation, Analytics, and API Integration Service for SmartRoute AI
 * 
 * Features:
 * - Real-time connection to Python FastAPI backend (A*, Dijkstra, BFS, DFS)
 * - Converts GPS coordinates to real road network geometry and turn-by-turn steps
 * - Provides side-by-side comparison between Fastest and Shortest routes
 * - Manages saved route bookmarks and history with MongoDB Atlas
 * - Graceful local fallback for offline/disconnected demo scenarios
 */

import { calculateHaversineDistanceKm } from '../utils/geoUtils';

// Backend API URL: configurable via VITE_API_URL or defaults to localhost:8000
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Normalizes backend RouteDetailSchema (snake_case) into frontend camelCase format
 */
export function normalizeBackendRoute(routeObj, preference) {
  if (!routeObj) return null;

  const pref = routeObj.preference || preference || 'fastest';
  const isFastest = pref === 'fastest';
  const distNum = typeof routeObj.numeric_distance_km === 'number'
    ? routeObj.numeric_distance_km
    : parseFloat(routeObj.distance_km) || 0.0;

  const steps = (routeObj.itinerary_steps || []).map((step, idx) => ({
    id: step.id || idx + 1,
    instruction: step.instruction || 'Proceed along path',
    distance: step.distance || '',
    time: step.time || ''
  }));

  return {
    id: pref,
    preference: pref,
    preferenceName: routeObj.preference_name || (isFastest ? 'Fastest Route' : 'Shortest Route'),
    badge: routeObj.badge || (isFastest ? 'Optimized for Travel Time (A*)' : 'Optimized for Distance (A*)'),
    distanceKm: routeObj.distance_km || `${distNum.toFixed(1)} km`,
    numericDistanceKm: distNum,
    estimatedTimeMin: routeObj.estimated_time_min || Math.max(1, Math.round(distNum / 35 * 60)),
    estimatedFuelLiters: routeObj.estimated_fuel_liters || `${(distNum * 0.08).toFixed(2)} L`,
    avgSpeedKmh: routeObj.avg_speed_kmh || (isFastest ? '38 km/h' : '26 km/h'),
    routeColor: routeObj.route_color || (isFastest ? '#06b6d4' : '#3b82f6'),
    routeType: routeObj.route_type || 'road_network',
    isStraightLine: Boolean(routeObj.is_straight_line),
    isSimulated: Boolean(routeObj.is_simulated),
    trafficLevel: routeObj.traffic_level || 'low',
    trafficStatusText: routeObj.traffic_status_text || 'Baseline OSM speed estimate',
    routeTypeDescription: routeObj.route_description || 'Computed via A* search on OSM road network.',
    algorithmUsed: routeObj.algorithm_used || 'A*',
    dataSource: routeObj.data_source || 'OSM Driving Network',
    originCoords: routeObj.origin_coords || [],
    destinationCoords: routeObj.destination_coords || [],
    pathCoordinates: routeObj.path_coordinates || [],
    itinerarySteps: steps
  };
}

/**
 * Calls FastAPI backend to calculate real road route via A* or benchmark algorithms
 */
export async function fetchCalculatedRouteFromBackend({
  originCoords,
  destinationCoords,
  originName = 'Origin',
  destinationName = 'Destination',
  preference = 'fastest',
  algorithm = 'astar'
}) {
  if (!originCoords || !destinationCoords) {
    throw new Error('Both origin and destination coordinates are required.');
  }

  const payload = {
    origin_coords: [Number(originCoords[0]), Number(originCoords[1])],
    destination_coords: [Number(destinationCoords[0]), Number(destinationCoords[1])],
    origin_name: originName,
    destination_name: destinationName,
    preference: preference
  };

  const url = `${API_BASE_URL}/api/calculate-route?algorithm=${encodeURIComponent(algorithm)}`;

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    let errorMsg = `Server error (${response.status})`;
    try {
      const errData = await response.json();
      errorMsg = errData.detail || errData.message || errorMsg;
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }

  const data = await response.json();
  const primaryNormalized = normalizeBackendRoute(data.route, preference);
  const altPref = preference === 'fastest' ? 'shortest' : 'fastest';
  const altNormalized = data.alternative_route
    ? normalizeBackendRoute(data.alternative_route, altPref)
    : null;

  const fastestRoute = preference === 'fastest' ? primaryNormalized : altNormalized;
  const shortestRoute = preference === 'shortest' ? primaryNormalized : altNormalized;

  return {
    fastest: fastestRoute,
    shortest: shortestRoute,
    active: primaryNormalized,
    activePreference: preference,
    executionTimeMs: data.execution_time_ms,
    isRealRoadNetwork: true
  };
}

/**
 * Local fallback route calculator if backend is temporarily disconnected
 */
export function calculateLocalFallbackRoute({
  originCoords,
  destinationCoords,
  originName = 'Origin',
  destinationName = 'Destination',
  activePreference = 'fastest'
}) {
  const straightLineKm = calculateHaversineDistanceKm(originCoords, destinationCoords);
  const makeRoute = (pref) => {
    const prefIsFast = pref === 'fastest';
    const dist = Number((straightLineKm * (prefIsFast ? 1.28 : 1.14)).toFixed(1));
    const spd = prefIsFast ? 38 : 26;
    const tMin = Math.max(2, Math.round((dist / spd) * 60));

    return {
      id: pref,
      preference: pref,
      preferenceName: prefIsFast ? 'Fastest Route (Offline)' : 'Shortest Route (Offline)',
      badge: prefIsFast ? 'Optimized for Travel Time' : 'Optimized for Distance',
      distanceKm: `${dist} km`,
      numericDistanceKm: dist,
      estimatedTimeMin: tMin,
      estimatedFuelLiters: `${(dist * 0.08).toFixed(2)} L`,
      avgSpeedKmh: `${spd} km/h`,
      routeColor: prefIsFast ? '#06b6d4' : '#3b82f6',
      routeType: 'simulated_corridor',
      isStraightLine: false,
      isSimulated: true,
      trafficLevel: 'low',
      trafficStatusText: 'Offline baseline estimates',
      routeTypeDescription: `Offline preview connecting ${originName} and ${destinationName}. Run backend for real-world OSM road routing.`,
      algorithmUsed: 'A* (Offline Fallback)',
      dataSource: 'Local Geometry Approximation',
      originCoords,
      destinationCoords,
      pathCoordinates: [originCoords, destinationCoords],
      itinerarySteps: [
        { id: 1, instruction: `Depart from ${originName}`, distance: '0 m', time: '0 min' },
        { id: 2, instruction: `Proceed toward ${destinationName}`, distance: `${dist} km`, time: `${tMin} min` },
        { id: 3, instruction: `Arrive at destination: ${destinationName}`, distance: '0 m', time: 'Arrival' }
      ]
    };
  };

  const fastest = makeRoute('fastest');
  const shortest = makeRoute('shortest');
  const active = activePreference === 'shortest' ? shortest : fastest;

  return {
    fastest,
    shortest,
    active,
    activePreference,
    isRealRoadNetwork: false
  };
}

/**
 * Unified calculation function that attempts backend API first, falling back to local
 */
export async function calculateAllRouteOptions({
  originCoords,
  destinationCoords,
  originName = 'Origin',
  destinationName = 'Destination',
  activePreference = 'fastest'
}) {
  try {
    const result = await fetchCalculatedRouteFromBackend({
      originCoords,
      destinationCoords,
      originName,
      destinationName,
      preference: activePreference
    });
    return result;
  } catch (err) {
    console.warn('Backend route calculation unavailable, using fallback:', err.message);
    const fallback = calculateLocalFallbackRoute({
      originCoords,
      destinationCoords,
      originName,
      destinationName,
      activePreference
    });
    fallback.errorNotice = err.message;
    return fallback;
  }
}

/**
 * Save route bookmark to MongoDB Atlas via backend
 */
export async function saveRouteToBackend(routeData) {
  const payload = {
    origin_name: routeData.originName || routeData.origin,
    origin_coords: routeData.originCoords,
    destination_name: routeData.destinationName || routeData.destination,
    destination_coords: routeData.destinationCoords,
    preference: routeData.preference || 'fastest',
    distance_km: Number(routeData.numericDistanceKm || parseFloat(routeData.distanceKm) || 0),
    estimated_time_min: Number(routeData.estimatedTimeMin || 0)
  };

  const res = await fetch(`${API_BASE_URL}/api/routes/save`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    throw new Error('Failed to save route to database.');
  }
  return await res.json();
}

/**
 * Retrieve saved route bookmarks from MongoDB Atlas
 */
export async function fetchSavedRoutesFromBackend() {
  const res = await fetch(`${API_BASE_URL}/api/routes/saved`);
  if (!res.ok) throw new Error('Failed to fetch saved routes.');
  return await res.json();
}

/**
 * Delete a saved route bookmark from MongoDB Atlas
 */
export async function deleteSavedRouteFromBackend(routeId) {
  const res = await fetch(`${API_BASE_URL}/api/routes/saved/${routeId}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Failed to delete route.');
  return await res.json();
}

/**
 * Retrieve recent route calculation history from MongoDB Atlas
 */
export async function fetchRouteHistoryFromBackend() {
  const res = await fetch(`${API_BASE_URL}/api/routes/history?limit=15`);
  if (!res.ok) throw new Error('Failed to fetch route history.');
  return await res.json();
}
