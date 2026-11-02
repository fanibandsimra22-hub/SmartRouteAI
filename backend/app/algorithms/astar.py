"""
astar.py

SmartRoute AI – A* (A-Star) Pathfinding Algorithm
The recommended default navigation algorithm for SmartRoute AI.

Key Characteristics:
- Informed best-first search guided by f(n) = g(n) + h(n).
- g(n): Actual accumulated path cost from source to node n.
- h(n): Admissible lower-bound heuristic to goal:
    * Shortest distance routing: Straight-line geographic Haversine distance in meters.
    * Fastest time routing: Straight-line distance divided by maximum vehicle speed in m/s.
- Supports both MultiDiGraph (resolving parallel road edges) and standard DiGraph.
"""

import heapq
import time
import itertools
from typing import Any, Optional
import networkx as nx

from app.algorithms.common import (
    PathResult,
    astar_admissible_heuristic,
    get_best_edge,
    reconstruct_path_and_metrics,
)


def astar_path(
    graph: nx.Graph,
    source: Any,
    target: Any,
    weight: str = "length",
    max_speed_kmh: Optional[float] = None
) -> PathResult:
    """
    Computes the optimal path from source to target using the A* search algorithm.

    Args:
        graph: NetworkX MultiDiGraph or DiGraph containing road network nodes and edges.
        source: Origin node ID.
        target: Destination node ID.
        weight: Optimization metric ('length' for shortest distance, 'travel_time' for fastest route).
        max_speed_kmh: Maximum vehicle speed limit in km/h used for the fastest-time heuristic.

    Returns:
        PathResult: Standardized result containing node path, distance, time, and performance metrics.
    """
    t_start = time.perf_counter()

    # 1. Input Validation
    if graph is None or len(graph.nodes) == 0:
        return PathResult(
            algorithm="A*",
            route_found=False,
            path=[],
            total_distance_m=0.0,
            estimated_travel_time_s=0.0,
            explored_nodes_count=0,
            execution_time_ms=0.0,
            weight_used=weight,
            message="Graph is empty or uninitialized."
        )

    if source not in graph.nodes:
        return PathResult(
            algorithm="A*",
            route_found=False,
            path=[],
            total_distance_m=0.0,
            estimated_travel_time_s=0.0,
            explored_nodes_count=0,
            execution_time_ms=round((time.perf_counter() - t_start) * 1000, 3),
            weight_used=weight,
            message=f"Starting location node {source} was not found in the road network."
        )

    if target not in graph.nodes:
        return PathResult(
            algorithm="A*",
            route_found=False,
            path=[],
            total_distance_m=0.0,
            estimated_travel_time_s=0.0,
            explored_nodes_count=0,
            execution_time_ms=round((time.perf_counter() - t_start) * 1000, 3),
            weight_used=weight,
            message=f"Destination node {target} was not found in the road network."
        )

    # 2. Edge Case: Source is identical to Target
    if source == target:
        t_elapsed = (time.perf_counter() - t_start) * 1000.0
        return PathResult(
            algorithm="A*",
            route_found=True,
            path=[source],
            total_distance_m=0.0,
            estimated_travel_time_s=0.0,
            explored_nodes_count=1,
            execution_time_ms=round(t_elapsed, 3),
            weight_used=weight,
            message="Origin and destination are the exact same location."
        )

    # 3. A* Search Data Structures
    counter = itertools.count()  # Tie-breaker for min-heap
    open_heap = []
    
    # g_score: minimum recorded cost to reach each node from source
    g_score = {source: 0.0}
    
    # Initial heuristic from source to target
    h_start = astar_admissible_heuristic(graph, source, target, weight, max_speed_kmh)
    f_score = {source: h_start}

    # Heap entries: (f_score, count, node_id)
    heapq.heappush(open_heap, (h_start, next(counter), source))

    parent_map = {source: None}
    closed_set = set()
    explored_count = 0

    # 4. A* Priority Queue Traversal Loop
    while open_heap:
        current_f, _, current = heapq.heappop(open_heap)

        if current in closed_set:
            continue

        closed_set.add(current)
        explored_count += 1

        # Goal Reached!
        if current == target:
            break

        current_g = g_score[current]

        # Explore outgoing neighbors
        neighbors = graph.neighbors(current) if not graph.is_directed() else graph.successors(current)

        for neighbor in neighbors:
            if neighbor in closed_set:
                continue

            # MultiDiGraph edge resolution: pick minimum weight among parallel edges
            edge_weight, _ = get_best_edge(graph, current, neighbor, weight)
            tentative_g = current_g + edge_weight

            if tentative_g < g_score.get(neighbor, float("inf")):
                g_score[neighbor] = tentative_g
                h_val = astar_admissible_heuristic(graph, neighbor, target, weight, max_speed_kmh)
                f_val = tentative_g + h_val
                f_score[neighbor] = f_val
                parent_map[neighbor] = current

                heapq.heappush(open_heap, (f_val, next(counter), neighbor))

    t_elapsed = (time.perf_counter() - t_start) * 1000.0

    # 5. Check if Target was reached
    if target not in closed_set and target not in parent_map:
        return PathResult(
            algorithm="A*",
            route_found=False,
            path=[],
            total_distance_m=0.0,
            estimated_travel_time_s=0.0,
            explored_nodes_count=explored_count,
            execution_time_ms=round(t_elapsed, 3),
            weight_used=weight,
            message=f"No viable driving road route exists between node {source} and node {target}."
        )

    # 6. Reconstruct complete node sequence and real road distance/travel time metrics
    path, dist_m, time_s = reconstruct_path_and_metrics(graph, parent_map, source, target, weight)

    if not path:
        return PathResult(
            algorithm="A*",
            route_found=False,
            path=[],
            total_distance_m=0.0,
            estimated_travel_time_s=0.0,
            explored_nodes_count=explored_count,
            execution_time_ms=round(t_elapsed, 3),
            weight_used=weight,
            message="Failed to reconstruct road route from path parent pointers."
        )

    return PathResult(
        algorithm="A*",
        route_found=True,
        path=path,
        total_distance_m=dist_m,
        estimated_travel_time_s=time_s,
        explored_nodes_count=explored_count,
        execution_time_ms=round(t_elapsed, 3),
        weight_used=weight,
        message="Optimal route successfully calculated using A*."
    )

