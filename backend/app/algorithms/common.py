"""
common.py

SmartRoute AI – Shared Algorithm Helpers & Result Structure
Provides unified result schemas, edge traversal resolution (handling MultiDiGraph parallel edges),
Haversine heuristics, and path metric calculations.
"""

import math
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Tuple, Optional
import networkx as nx


@dataclass
class PathResult:
    """
    Standardized result payload returned by all SmartRoute AI pathfinding algorithms.
    """
    algorithm: str
    route_found: bool
    path: List[Any]
    total_distance_m: float
    estimated_travel_time_s: float
    explored_nodes_count: int
    execution_time_ms: float
    weight_used: str
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts the PathResult dataclass to a standard Python dictionary."""
        return asdict(self)


def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes the great-circle geographic distance between two GPS coordinates in meters.
    Formula: d = 2 * R * arcsin(sqrt(sin²(Δlat/2) + cos(lat1)*cos(lat2)*sin²(Δlon/2)))
    """
    earth_radius_m = 6371000.0  # Mean radius of Earth
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
    return earth_radius_m * c


def get_graph_admissibility_factors(graph: nx.Graph) -> Tuple[float, float]:
    """
    Computes conservative lower-bound heuristic factors for a graph:
    1. alpha: Distance scaling factor = min(1.0, min(length / haversine_dist) across valid edges)
       Guarantees that alpha * haversine(u, v) <= stored_road_length(u, v) for every edge.
       Edges with zero geographic displacement (haversine <= 1e-4) or non-positive lengths
       are safely ignored to prevent division-by-zero or non-physical distortions.
    2. max_speed_ms: Maximum effective vehicle speed across all valid edges (in m/s).
       Derived from edge length / travel_time and speed_kph.
       Guarantees that (alpha * haversine) / max_speed_ms <= stored_travel_time(u, v).

    Caches the calculated factors in graph.graph['_admissibility_factors'] to avoid
    re-iterating edges on every heuristic call.

    Returns:
        Tuple[float, float]: (alpha, max_speed_ms)
    """
    if graph is None:
        return 1.0, 35.0 * 1000.0 / 3600.0

    factors = graph.graph.get("_admissibility_factors")
    if factors is not None:
        return factors

    ratios: List[float] = []
    speeds_ms: List[float] = []

    # Iterate over all edges (supporting both MultiDiGraph and standard DiGraph)
    edge_iter = graph.edges(data=True, keys=True) if graph.is_multigraph() else graph.edges(data=True)

    for edge in edge_iter:
        if graph.is_multigraph():
            u, v, _, data = edge
        else:
            u, v, data = edge

        node_u = graph.nodes.get(u, {})
        node_v = graph.nodes.get(v, {})

        # Check coordinates validity
        if "y" in node_u and "x" in node_u and "y" in node_v and "x" in node_v:
            h_dist = haversine_distance_m(
                float(node_u["y"]), float(node_u["x"]),
                float(node_v["y"]), float(node_v["x"])
            )
            length = float(data.get("length", 0.0))

            # Ignore self-loops or zero-displacement segments (h_dist <= 1e-3)
            # and ignore non-positive road lengths
            if h_dist > 1e-3 and length > 0.0:
                ratios.append(length / h_dist)

        # Check speed / travel time validity
        length = float(data.get("length", 0.0))
        travel_time = float(data.get("travel_time", 0.0))
        speed_kph = data.get("speed_kph")

        if length > 0.0 and travel_time > 0.0:
            speeds_ms.append(length / travel_time)

        if speed_kph is not None:
            try:
                speeds_ms.append((float(speed_kph) * 1000.0) / 3600.0)
            except (ValueError, TypeError):
                pass

    alpha = min(1.0, min(ratios)) if ratios else 1.0
    # Safe fallback max speed is 50.0 km/h (13.89 m/s)
    max_v = max(speeds_ms) if speeds_ms else (50.0 * 1000.0 / 3600.0)

    factors = (alpha, max_v)
    try:
        graph.graph["_admissibility_factors"] = factors
    except Exception:
        pass

    return factors


def astar_admissible_heuristic(
    graph: nx.Graph,
    current_node: Any,
    target_node: Any,
    weight_attr: str = "length",
    max_speed_kmh: Optional[float] = None
) -> float:
    """
    Admissible and monotonic lower-bound heuristic for A* pathfinding.

    Guarantees:
    - When weight_attr == 'length':
        Returns alpha * haversine_distance(current, target) in meters.
        Because alpha <= min(length / haversine) across all edges, alpha * haversine is a strict
        lower bound on the accumulated road length: h(u) <= h*(u) (strictly admissible).
    - When weight_attr == 'travel_time':
        Returns (alpha * haversine_distance) / max_effective_speed_ms in seconds.
        Because vehicle speed on any edge <= max_effective_speed_ms, this ratio is guaranteed
        to never overestimate the true remaining travel time: h(u) <= h*(u) (strictly admissible).
    """
    node_u = graph.nodes.get(current_node, {})
    node_t = graph.nodes.get(target_node, {})

    if "y" not in node_u or "x" not in node_u or "y" not in node_t or "x" not in node_t:
        return 0.0  # Admissible zero-heuristic fallback when coordinates are absent

    dist_m = haversine_distance_m(
        float(node_u["y"]), float(node_u["x"]),
        float(node_t["y"]), float(node_t["x"])
    )

    alpha, max_speed_ms = get_graph_admissibility_factors(graph)

    # Scale distance lower-bound by alpha
    scaled_dist_m = alpha * dist_m

    if weight_attr == "travel_time":
        if max_speed_kmh is not None:
            user_speed_ms = (max_speed_kmh * 1000.0) / 3600.0
            effective_speed_ms = max(max_speed_ms, user_speed_ms)
        else:
            effective_speed_ms = max_speed_ms

        return scaled_dist_m / max(0.1, effective_speed_ms)

    return scaled_dist_m


def get_best_edge(
    graph: nx.Graph,
    u: Any,
    v: Any,
    weight_attr: str = "length"
) -> Tuple[float, Dict[str, Any]]:
    """
    Resolves the best edge between node u and node v.
    Correctly accounts for parallel edges in NetworkX MultiDiGraph by selecting
    the edge that minimizes the specified weight_attr.

    Returns:
        Tuple[float, Dict[str, Any]]: (best_weight_value, best_edge_data_dict)
    """
    edge_container = graph[u][v]

    # Handle MultiDiGraph / MultiGraph (mapping of edge_key -> edge_data)
    if graph.is_multigraph():
        best_weight = float("inf")
        best_data: Dict[str, Any] = {}

        for edge_data in edge_container.values():
            weight_val = _extract_edge_weight(edge_data, weight_attr, graph, u, v)
            if weight_val < best_weight:
                best_weight = weight_val
                best_data = dict(edge_data)

        return best_weight, best_data

    # Handle standard DiGraph / Graph (direct edge_data dict)
    weight_val = _extract_edge_weight(edge_container, weight_attr, graph, u, v)
    return weight_val, dict(edge_container)


def _extract_edge_weight(
    edge_data: Dict[str, Any],
    weight_attr: str,
    graph: nx.Graph,
    u: Any,
    v: Any
) -> float:
    """
    Extracts numerical weight from an edge data dictionary with safe fallbacks.
    """
    val = edge_data.get(weight_attr)
    if val is not None:
        try:
            return float(val)
        except (ValueError, TypeError):
            pass

    # Safe fallbacks if specific attribute is missing
    if weight_attr == "travel_time":
        # Approximate from length and speed
        length_m = float(edge_data.get("length", 100.0))
        speed_kph = float(edge_data.get("speed_kph", 35.0))
        speed_ms = max(1.0, (speed_kph * 1000.0) / 3600.0)
        return length_m / speed_ms

    if weight_attr == "length":
        # Approximate from node coordinates if available
        node_u = graph.nodes.get(u, {})
        node_v = graph.nodes.get(v, {})
        if "y" in node_u and "x" in node_u and "y" in node_v and "x" in node_v:
            return haversine_distance_m(
                float(node_u["y"]), float(node_u["x"]),
                float(node_v["y"]), float(node_v["x"])
            )
        return 100.0  # Nominal road segment length fallback

    return 1.0


def reconstruct_path_and_metrics(
    graph: nx.Graph,
    parent_map: Dict[Any, Any],
    source: Any,
    target: Any,
    weight_attr: str = "length"
) -> Tuple[List[Any], float, float]:
    """
    Reconstructs the node path from parent pointers and calculates exact physical road
    distance (in meters) and estimated travel time (in seconds) by summing the chosen edge attributes.

    Returns:
        Tuple[List[Any], float, float]: (node_path, total_distance_m, total_travel_time_s)
    """
    curr = target
    path: List[Any] = []

    while curr is not None:
        path.append(curr)
        curr = parent_map.get(curr)

    path.reverse()

    if not path or path[0] != source:
        return [], 0.0, 0.0

    total_distance_m = 0.0
    total_travel_time_s = 0.0

    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]
        _, edge_data = get_best_edge(graph, u, v, weight_attr)

        edge_length = float(edge_data.get("length", 0.0))
        edge_time = edge_data.get("travel_time")

        if edge_time is not None:
            edge_time_s = float(edge_time)
        else:
            speed_kph = float(edge_data.get("speed_kph", 35.0))
            speed_ms = max(1.0, (speed_kph * 1000.0) / 3600.0)
            edge_time_s = edge_length / speed_ms

        total_distance_m += edge_length
        total_travel_time_s += edge_time_s

    return path, round(total_distance_m, 2), round(total_travel_time_s, 2)
