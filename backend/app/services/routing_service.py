"""
routing_service.py

SmartRoute AI – Core Routing Engine Service
Coordinates nearest-node spatial mapping, pathfinding algorithm execution,
road-edge geometry reconstruction, turn-by-turn instruction synthesis,
traffic evaluation, and MongoDB history persistence.
"""

import math
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
import networkx as nx
from shapely import wkt
from shapely.geometry import LineString

from app.services.graph_service import get_road_graph, get_nearest_node
from app.algorithms import astar_path, dijkstra_path, bfs_path, dfs_path
from app.algorithms.common import get_best_edge, PathResult, haversine_distance_m
from app.schemas.route_schema import (
    RouteCalculationRequest,
    RouteCalculationResponse,
    RouteDetailSchema,
    WaypointStepSchema,
)
from app.services.traffic_service import get_traffic_status_for_route
from app.database import db_manager

logger = logging.getLogger("smartroute.routing_service")


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates initial compass bearing (azimuth) from point 1 to point 2 in degrees [0, 360).
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
    bearing = math.degrees(math.atan2(y, x))
    return (bearing + 360.0) % 360.0


def describe_turn(bearing1: float, bearing2: float) -> str:
    """
    Determines relative turn instruction based on angular difference between bearings.
    """
    diff = (bearing2 - bearing1 + 180.0) % 360.0 - 180.0
    if abs(diff) <= 22.5:
        return "Continue straight on"
    elif 22.5 < diff <= 67.5:
        return "Slight right onto"
    elif 67.5 < diff <= 120.0:
        return "Turn right onto"
    elif diff > 120.0:
        return "Sharp right onto"
    elif -67.5 <= diff < -22.5:
        return "Slight left onto"
    elif -120.0 <= diff < -67.5:
        return "Turn left onto"
    else:
        return "Sharp left onto"


def extract_road_name(edge_data: Dict[str, Any]) -> str:
    """
    Extracts a readable street or highway name from OSM edge attributes.
    """
    name = edge_data.get("name")
    if isinstance(name, list) and name:
        return str(name[0])
    elif isinstance(name, str) and name.strip():
        return name.strip()
    
    ref = edge_data.get("ref")
    if isinstance(ref, list) and ref:
        return str(ref[0])
    elif isinstance(ref, str) and ref.strip():
        return ref.strip()

    highway = edge_data.get("highway")
    if isinstance(highway, str):
        return f"{highway.replace('_', ' ').title()} Link"
    
    return "Connecting Road"


def reconstruct_route_geometry_and_instructions(
    graph: nx.MultiDiGraph,
    path: List[Any],
    weight: str,
    origin_name: str,
    destination_name: str
) -> Tuple[List[List[float]], List[WaypointStepSchema], float, float]:
    """
    Extracts full curved geometry from road edges (handling LineString attributes and parallel edges)
    and synthesizes grouped turn-by-turn navigation instructions.
    
    Returns:
        (path_coordinates, itinerary_steps, total_distance_m, total_travel_time_s)
    """
    if not path or len(path) < 2:
        return [], [], 0.0, 0.0

    path_coordinates: List[List[float]] = []
    edge_segments: List[Dict[str, Any]] = []
    total_dist_m = 0.0
    total_time_s = 0.0

    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        best_cost, edge_data = get_best_edge(graph, u, v, weight_attr=weight)

        u_data = graph.nodes[u]
        v_data = graph.nodes[v]
        u_coord = [float(u_data.get("y", 0.0)), float(u_data.get("x", 0.0))]
        v_coord = [float(v_data.get("y", 0.0)), float(v_data.get("x", 0.0))]

        edge_dist = float(edge_data.get("length", 0.0))
        edge_time = float(edge_data.get("travel_time", edge_dist / 9.72))
        total_dist_m += edge_dist
        total_time_s += edge_time

        # Extract coordinate curve
        coords_for_edge: List[List[float]] = []
        geom = edge_data.get("geometry")

        if isinstance(geom, LineString):
            # Shapely coords: (lon, lat) -> convert to [lat, lon]
            coords_for_edge = [[float(pt[1]), float(pt[0])] for pt in geom.coords]
        elif isinstance(geom, str) and geom.startswith("LINESTRING"):
            try:
                parsed_geom = wkt.loads(geom)
                coords_for_edge = [[float(pt[1]), float(pt[0])] for pt in parsed_geom.coords]
            except Exception:
                coords_for_edge = [u_coord, v_coord]
        else:
            coords_for_edge = [u_coord, v_coord]

        # Append to continuous route path coordinates
        if not path_coordinates:
            path_coordinates.extend(coords_for_edge)
        else:
            # Avoid duplicate intermediate junctions
            path_coordinates.extend(coords_for_edge[1:])

        # Calculate segment bearing
        if len(coords_for_edge) >= 2:
            seg_bearing = calculate_bearing(
                coords_for_edge[0][0], coords_for_edge[0][1],
                coords_for_edge[-1][0], coords_for_edge[-1][1]
            )
        else:
            seg_bearing = 0.0

        edge_segments.append({
            "name": extract_road_name(edge_data),
            "distance_m": edge_dist,
            "travel_time_s": edge_time,
            "bearing": seg_bearing,
            "start_coord": coords_for_edge[0],
            "end_coord": coords_for_edge[-1]
        })

    # Group consecutive segments on the same street for clean, readable instructions
    itinerary_steps: List[WaypointStepSchema] = []
    step_id = 1

    # Step 1: Starting instruction
    if edge_segments:
        first_road = edge_segments[0]["name"]
        itinerary_steps.append(WaypointStepSchema(
            id=step_id,
            instruction=f"Depart from {origin_name} onto {first_road}",
            distance=f"{max(10, int(edge_segments[0]['distance_m']))} m",
            time=f"{max(1, int(edge_segments[0]['travel_time_s'] // 60))} min"
        ))
        step_id += 1

    current_group: Optional[Dict[str, Any]] = None

    for idx, seg in enumerate(edge_segments):
        if current_group is None:
            current_group = {
                "name": seg["name"],
                "distance_m": seg["distance_m"],
                "time_s": seg["travel_time_s"],
                "bearing": seg["bearing"],
                "initial_idx": idx
            }
        elif current_group["name"] == seg["name"]:
            current_group["distance_m"] += seg["distance_m"]
            current_group["time_s"] += seg["travel_time_s"]
        else:
            # Flush previous group as instruction
            turn_verb = "Follow"
            if current_group["initial_idx"] > 0:
                prev_bearing = edge_segments[current_group["initial_idx"] - 1]["bearing"]
                turn_verb = describe_turn(prev_bearing, current_group["bearing"])

            dist_str = f"{current_group['distance_m'] / 1000.0:.1f} km" if current_group['distance_m'] >= 1000 else f"{int(current_group['distance_m'])} m"
            time_min = max(1, math.ceil(current_group['time_s'] / 60.0))

            itinerary_steps.append(WaypointStepSchema(
                id=step_id,
                instruction=f"{turn_verb} {current_group['name']}",
                distance=dist_str,
                time=f"{time_min} min"
            ))
            step_id += 1

            current_group = {
                "name": seg["name"],
                "distance_m": seg["distance_m"],
                "time_s": seg["travel_time_s"],
                "bearing": seg["bearing"],
                "initial_idx": idx
            }

    # Flush final grouped segment
    if current_group:
        turn_verb = "Continue along"
        if current_group["initial_idx"] > 0:
            prev_bearing = edge_segments[current_group["initial_idx"] - 1]["bearing"]
            turn_verb = describe_turn(prev_bearing, current_group["bearing"])

        dist_str = f"{current_group['distance_m'] / 1000.0:.1f} km" if current_group['distance_m'] >= 1000 else f"{int(current_group['distance_m'])} m"
        time_min = max(1, math.ceil(current_group['time_s'] / 60.0))

        itinerary_steps.append(WaypointStepSchema(
            id=step_id,
            instruction=f"{turn_verb} {current_group['name']} toward destination area",
            distance=dist_str,
            time=f"{time_min} min"
        ))
        step_id += 1

    # Final arrival step
    itinerary_steps.append(WaypointStepSchema(
        id=step_id,
        instruction=f"Arrive at destination: {destination_name}",
        distance="0 m",
        time="Arrival"
    ))

    return path_coordinates, itinerary_steps, total_dist_m, total_time_s


async def build_route_detail(
    graph: nx.MultiDiGraph,
    path_result: PathResult,
    preference: str,
    algorithm_name: str,
    origin_name: str,
    destination_name: str,
    origin_coords: List[float],
    destination_coords: List[float]
) -> RouteDetailSchema:
    """
    Constructs a complete RouteDetailSchema instance from algorithm PathResult.
    """
    weight = "travel_time" if preference == "fastest" else "length"

    (
        path_coords,
        itinerary,
        total_dist_m,
        total_time_s
    ) = reconstruct_route_geometry_and_instructions(
        graph=graph,
        path=path_result.path,
        weight=weight,
        origin_name=origin_name,
        destination_name=destination_name
    )

    # Fallback to PathResult metrics if edge geometry reconstruction was empty
    final_dist_m = total_dist_m if total_dist_m > 0 else path_result.total_distance_m
    final_time_s = total_time_s if total_time_s > 0 else path_result.estimated_travel_time_s

    dist_km = round(final_dist_m / 1000.0, 2)
    time_min = max(1, int(round(final_time_s / 60.0)))
    avg_speed = round((dist_km / (time_min / 60.0)), 1) if time_min > 0 else 35.0
    est_fuel_liters = f"{dist_km * 0.08:.2f} L"

    # Evaluate traffic conditions (TomTom live check or baseline OSM)
    traffic_info = await get_traffic_status_for_route(path_coords, final_time_s)

    pref_name = "Fastest Route" if preference == "fastest" else "Shortest Route"
    badge = (
        f"Optimized for Travel Time ({algorithm_name})"
        if preference == "fastest"
        else f"Optimized for Distance ({algorithm_name})"
    )
    route_color = "#06b6d4" if preference == "fastest" else "#3b82f6"

    description = (
        f"Real-world road navigation computed via {algorithm_name} across the Central Goa OSM network. "
        f"Explored {path_result.explored_nodes_count} intersections in {path_result.execution_time_ms:.1f}ms."
    )

    return RouteDetailSchema(
        id=preference,
        preference=preference,
        preference_name=pref_name,
        badge=badge,
        distance_km=f"{dist_km} km",
        numeric_distance_km=dist_km,
        estimated_time_min=time_min + traffic_info.get("delay_minutes", 0),
        estimated_fuel_liters=est_fuel_liters,
        avg_speed_kmh=f"{avg_speed} km/h",
        route_color=route_color,
        route_type="road_network",
        is_straight_line=False,
        is_simulated=False,
        traffic_level=traffic_info.get("traffic_level", "low"),
        traffic_status_text=traffic_info.get("traffic_status_text", "Baseline OSM Speeds"),
        route_description=description,
        algorithm_used=algorithm_name,
        data_source="OSM Driving Network (OSMnx / NetworkX)",
        origin_coords=origin_coords,
        destination_coords=destination_coords,
        path_coordinates=path_coords if path_coords else [origin_coords, destination_coords],
        itinerary_steps=itinerary
    )


async def compute_navigation_route(
    request: RouteCalculationRequest,
    algorithm: str = "astar"
) -> RouteCalculationResponse:
    """
    Main entry point for route calculation requests.
    Calculates primary route and alternative comparison route.
    """
    t_start = time.perf_counter()

    graph = get_road_graph(auto_load=True)
    if graph is None or len(graph.nodes) == 0:
        raise RuntimeError("Road network graph could not be loaded into memory.")

    origin_lat, origin_lon = request.origin_coords[0], request.origin_coords[1]
    dest_lat, dest_lon = request.destination_coords[0], request.destination_coords[1]

    # Map GPS coordinates to nearest road network nodes
    source_node = get_nearest_node(graph, origin_lat, origin_lon)
    target_node = get_nearest_node(graph, dest_lat, dest_lon)

    # Validate spatial snap distance to avoid misleading routes for points outside corridor coverage
    max_snap_distance_m = 3500.0  # 3.5 km corridor snap threshold
    src_data = graph.nodes[source_node]
    src_dist = haversine_distance_m(
        origin_lat, origin_lon,
        float(src_data.get("y", origin_lat)), float(src_data.get("x", origin_lon))
    )
    if src_dist > max_snap_distance_m:
        raise ValueError(
            f"Origin '{request.origin_name or 'Origin'}' is approximately {src_dist / 1000.0:.1f} km away from the nearest supported road network. "
            f"SmartRoute AI Central Goa coverage currently spans the Panaji – Miramar – Dona Paula – Bambolim – PCCE Verna corridor."
        )

    tgt_data = graph.nodes[target_node]
    tgt_dist = haversine_distance_m(
        dest_lat, dest_lon,
        float(tgt_data.get("y", dest_lat)), float(tgt_data.get("x", dest_lon))
    )
    if tgt_dist > max_snap_distance_m:
        raise ValueError(
            f"Destination '{request.destination_name or 'Destination'}' is approximately {tgt_dist / 1000.0:.1f} km away from the nearest supported road network. "
            f"SmartRoute AI Central Goa coverage currently spans the Panaji – Miramar – Dona Paula – Bambolim – PCCE Verna corridor."
        )

    primary_pref = request.preference # 'fastest' or 'shortest'
    primary_weight = "travel_time" if primary_pref == "fastest" else "length"

    algo_clean = algorithm.lower().strip()

    # Execute selected pathfinding algorithm
    if algo_clean == "dijkstra":
        res_primary = dijkstra_path(graph, source_node, target_node, weight=primary_weight)
        algo_label = "Dijkstra"
    elif algo_clean == "bfs":
        res_primary = bfs_path(graph, source_node, target_node)
        algo_label = "BFS (Unweighted Demo)"
    elif algo_clean == "dfs":
        res_primary = dfs_path(graph, source_node, target_node)
        algo_label = "DFS (Unweighted Demo)"
    else:
        # Default: A*
        res_primary = astar_path(graph, source_node, target_node, weight=primary_weight)
        algo_label = "A*"

    if not res_primary.route_found or len(res_primary.path) == 0:
        raise ValueError(
            f"No drivable road route found between '{request.origin_name}' and '{request.destination_name}'. "
            f"The locations may be on disconnected road networks or outside the covered Central Goa boundary."
        )

    # Build primary route detail
    route_primary = await build_route_detail(
        graph=graph,
        path_result=res_primary,
        preference=primary_pref,
        algorithm_name=algo_label,
        origin_name=request.origin_name or "Origin",
        destination_name=request.destination_name or "Destination",
        origin_coords=request.origin_coords,
        destination_coords=request.destination_coords
    )

    # Build alternative comparison route (opposite preference using A*)
    alt_pref = "shortest" if primary_pref == "fastest" else "fastest"
    alt_weight = "length" if alt_pref == "shortest" else "travel_time"
    res_alt = astar_path(graph, source_node, target_node, weight=alt_weight)

    alternative_route: Optional[RouteDetailSchema] = None
    if res_alt.route_found and len(res_alt.path) > 0:
        alternative_route = await build_route_detail(
            graph=graph,
            path_result=res_alt,
            preference=alt_pref,
            algorithm_name="A*",
            origin_name=request.origin_name or "Origin",
            destination_name=request.destination_name or "Destination",
            origin_coords=request.origin_coords,
            destination_coords=request.destination_coords
        )

    total_exec_ms = round((time.perf_counter() - t_start) * 1000.0, 2)

    # Record to MongoDB route history
    try:
        history_col = db_manager.get_collection("route_history")
        history_doc = {
            "origin_name": request.origin_name,
            "origin_coords": request.origin_coords,
            "destination_name": request.destination_name,
            "destination_coords": request.destination_coords,
            "preference": primary_pref,
            "algorithm_used": algo_label,
            "distance_km": route_primary.numeric_distance_km,
            "estimated_time_min": route_primary.estimated_time_min,
            "traffic_level": route_primary.traffic_level,
            "execution_time_ms": total_exec_ms,
            "user_id": "guest",
            "created_at": time.time()
        }
        history_col.insert_one(history_doc)
    except Exception as db_err:
        logger.warning(f"Could not log route history to database: {db_err}")

    return RouteCalculationResponse(
        status="success",
        active_preference=primary_pref,
        route=route_primary,
        alternative_route=alternative_route,
        execution_time_ms=total_exec_ms
    )
