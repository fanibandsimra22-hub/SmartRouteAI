"""
bfs.py

SmartRoute AI – Breadth-First Search (BFS) Algorithm
Finds the path with the fewest number of road intersections / edge hops.

Important Engineering Note:
BFS treats all edges as unweighted (cost = 1 hop).
It minimizes the NUMBER OF ROAD SEGMENTS, but DOES NOT OPTIMIZE physical road distance
or travel time. A 2-hop highway bypass might be 15 km, while a 4-hop city route might be 4 km.
BFS is valuable as an educational graph traversal benchmark.
"""

from collections import deque
import time
from typing import Any
import networkx as nx

from app.algorithms.common import (
    PathResult,
    reconstruct_path_and_metrics,
)


def bfs_path(
    graph: nx.Graph,
    source: Any,
    target: Any
) -> PathResult:
    """
    Computes a path with the minimum number of edge hops using Breadth-First Search.

    Args:
        graph: NetworkX MultiDiGraph or DiGraph.
        source: Origin node ID.
        target: Destination node ID.

    Returns:
        PathResult: Standardized result containing node path, distance, time, and performance metrics.
    """
    t_start = time.perf_counter()

    # 1. Input Validation
    if graph is None or len(graph.nodes) == 0:
        return PathResult(
            algorithm="BFS",
            route_found=False,
            path=[],
            total_distance_m=0.0,
            estimated_travel_time_s=0.0,
            explored_nodes_count=0,
            execution_time_ms=0.0,
            weight_used="unweighted (hop count)",
            message="Graph is empty or uninitialized."
        )

    if source not in graph.nodes:
        return PathResult(
            algorithm="BFS",
            route_found=False,
            path=[],
            total_distance_m=0.0,
            estimated_travel_time_s=0.0,
            explored_nodes_count=0,
            execution_time_ms=round((time.perf_counter() - t_start) * 1000, 3),
            weight_used="unweighted (hop count)",
            message=f"Starting location node {source} was not found in the road network."
        )

    if target not in graph.nodes:
        return PathResult(
            algorithm="BFS",
            route_found=False,
            path=[],
            total_distance_m=0.0,
            estimated_travel_time_s=0.0,
            explored_nodes_count=0,
            execution_time_ms=round((time.perf_counter() - t_start) * 1000, 3),
            weight_used="unweighted (hop count)",
            message=f"Destination node {target} was not found in the road network."
        )

    # 2. Edge Case: Source is identical to Target
    if source == target:
        t_elapsed = (time.perf_counter() - t_start) * 1000.0
        return PathResult(
            algorithm="BFS",
            route_found=True,
            path=[source],
            total_distance_m=0.0,
            estimated_travel_time_s=0.0,
            explored_nodes_count=1,
            execution_time_ms=round(t_elapsed, 3),
            weight_used="unweighted (hop count)",
            message="Origin and destination are the exact same location."
        )

    # 3. BFS Queue Data Structure (FIFO)
    queue = deque([source])
    visited = {source}
    parent_map = {source: None}
    explored_count = 0

    target_found = False

    # 4. Level-by-Level Exploration Loop
    while queue:
        current = queue.popleft()
        explored_count += 1

        if current == target:
            target_found = True
            break

        neighbors = graph.neighbors(current) if not graph.is_directed() else graph.successors(current)

        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                parent_map[neighbor] = current
                queue.append(neighbor)

                if neighbor == target:
                    target_found = True
                    explored_count += 1
                    break

        if target_found:
            break

    t_elapsed = (time.perf_counter() - t_start) * 1000.0

    # 5. Check if Target was reached
    if not target_found or target not in parent_map:
        return PathResult(
            algorithm="BFS",
            route_found=False,
            path=[],
            total_distance_m=0.0,
            estimated_travel_time_s=0.0,
            explored_nodes_count=explored_count,
            execution_time_ms=round(t_elapsed, 3),
            weight_used="unweighted (hop count)",
            message=f"No viable driving road route exists between node {source} and node {target}."
        )

    # 6. Reconstruct complete node sequence and real road distance/travel time metrics
    path, dist_m, time_s = reconstruct_path_and_metrics(graph, parent_map, source, target, weight_attr="length")

    return PathResult(
        algorithm="BFS",
        route_found=True,
        path=path,
        total_distance_m=dist_m,
        estimated_travel_time_s=time_s,
        explored_nodes_count=explored_count,
        execution_time_ms=round(t_elapsed, 3),
        weight_used="unweighted (hop count)",
        message="Route found using BFS (optimized for minimum edge hops; not distance or travel time)."
    )

