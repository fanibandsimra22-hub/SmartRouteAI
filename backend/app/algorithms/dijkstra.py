"""
dijkstra.py

SmartRoute AI – Dijkstra's Shortest Path Algorithm
The classic shortest-path algorithm used as an exact optimal benchmark.

Key Characteristics:
- Uniform-cost search (equivalent to A* with h(n) = 0).
- Guarantees the shortest path on graphs with non-negative edge weights.
- Explores nodes outward in circular wavefronts of increasing cost.
- Supports both MultiDiGraph (resolving parallel road edges) and standard DiGraph.
"""

import heapq
import time
import itertools
from typing import Any
import networkx as nx

from app.algorithms.common import (
    PathResult,
    get_best_edge,
    reconstruct_path_and_metrics,
)


def dijkstra_path(
    graph: nx.Graph,
    source: Any,
    target: Any,
    weight: str = "length"
) -> PathResult:
    """
    Computes the shortest path from source to target using Dijkstra's algorithm.

    Args:
        graph: NetworkX MultiDiGraph or DiGraph containing road network nodes and edges.
        source: Origin node ID.
        target: Destination node ID.
        weight: Optimization metric ('length' for shortest distance, 'travel_time' for fastest route).

    Returns:
        PathResult: Standardized result containing node path, distance, time, and performance metrics.
    """
    t_start = time.perf_counter()

    # 1. Input Validation
    if graph is None or len(graph.nodes) == 0:
        return PathResult(
            algorithm="Dijkstra",
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
            algorithm="Dijkstra",
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
            algorithm="Dijkstra",
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
            algorithm="Dijkstra",
            route_found=True,
            path=[source],
            total_distance_m=0.0,
            estimated_travel_time_s=0.0,
            explored_nodes_count=1,
            execution_time_ms=round(t_elapsed, 3),
            weight_used=weight,
            message="Origin and destination are the exact same location."
        )

    # 3. Dijkstra Data Structures
    counter = itertools.count()  # Tie-breaker for min-heap
    pq = []
    
    # dist: tracks shortest known distance from source to each node
    dist = {source: 0.0}
    heapq.heappush(pq, (0.0, next(counter), source))

    parent_map = {source: None}
    visited = set()
    explored_count = 0

    # 4. Priority Queue Traversal Loop
    while pq:
        current_dist, _, current = heapq.heappop(pq)

        if current in visited:
            continue

        visited.add(current)
        explored_count += 1

        # Goal Reached!
        if current == target:
            break

        # Explore outgoing neighbors
        neighbors = graph.neighbors(current) if not graph.is_directed() else graph.successors(current)

        for neighbor in neighbors:
            if neighbor in visited:
                continue

            # MultiDiGraph edge resolution: pick minimum weight among parallel edges
            edge_weight, _ = get_best_edge(graph, current, neighbor, weight)
            new_dist = current_dist + edge_weight

            if new_dist < dist.get(neighbor, float("inf")):
                dist[neighbor] = new_dist
                parent_map[neighbor] = current
                heapq.heappush(pq, (new_dist, next(counter), neighbor))

    t_elapsed = (time.perf_counter() - t_start) * 1000.0

    # 5. Check if Target was reached
    if target not in visited and target not in parent_map:
        return PathResult(
            algorithm="Dijkstra",
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
            algorithm="Dijkstra",
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
        algorithm="Dijkstra",
        route_found=True,
        path=path,
        total_distance_m=dist_m,
        estimated_travel_time_s=time_s,
        explored_nodes_count=explored_count,
        execution_time_ms=round(t_elapsed, 3),
        weight_used=weight,
        message="Optimal route successfully calculated using Dijkstra's algorithm."
    )

