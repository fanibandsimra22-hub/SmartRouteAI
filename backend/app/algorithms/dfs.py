"""
dfs.py

SmartRoute AI – Depth-First Search (DFS) Algorithm
Explores deeply along each branch before backtracking.

Important Engineering Note:
DFS DOES NOT guarantee the shortest distance, the fastest travel time, or the fewest hops.
It simply returns the first valid path it stumbles upon while traversing deep branches.
In city road networks, DFS may choose an erratic, winding route. It is provided as an
educational algorithm comparison baseline to demonstrate why informed search (like A*) is essential.
"""

import time
from typing import Any
import networkx as nx

from app.algorithms.common import (
    PathResult,
    reconstruct_path_and_metrics,
)


def dfs_path(
    graph: nx.Graph,
    source: Any,
    target: Any
) -> PathResult:
    """
    Finds a path from source to target using an iterative Depth-First Search.

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
            algorithm="DFS",
            route_found=False,
            path=[],
            total_distance_m=0.0,
            estimated_travel_time_s=0.0,
            explored_nodes_count=0,
            execution_time_ms=0.0,
            weight_used="unweighted (depth exploration)",
            message="Graph is empty or uninitialized."
        )

    if source not in graph.nodes:
        return PathResult(
            algorithm="DFS",
            route_found=False,
            path=[],
            total_distance_m=0.0,
            estimated_travel_time_s=0.0,
            explored_nodes_count=0,
            execution_time_ms=round((time.perf_counter() - t_start) * 1000, 3),
            weight_used="unweighted (depth exploration)",
            message=f"Starting location node {source} was not found in the road network."
        )

    if target not in graph.nodes:
        return PathResult(
            algorithm="DFS",
            route_found=False,
            path=[],
            total_distance_m=0.0,
            estimated_travel_time_s=0.0,
            explored_nodes_count=0,
            execution_time_ms=round((time.perf_counter() - t_start) * 1000, 3),
            weight_used="unweighted (depth exploration)",
            message=f"Destination node {target} was not found in the road network."
        )

    # 2. Edge Case: Source is identical to Target
    if source == target:
        t_elapsed = (time.perf_counter() - t_start) * 1000.0
        return PathResult(
            algorithm="DFS",
            route_found=True,
            path=[source],
            total_distance_m=0.0,
            estimated_travel_time_s=0.0,
            explored_nodes_count=1,
            execution_time_ms=round(t_elapsed, 3),
            weight_used="unweighted (depth exploration)",
            message="Origin and destination are the exact same location."
        )

    # 3. Iterative DFS using LIFO stack (avoids Python recursion limits)
    # Stack stores tuples: (current_node, parent_node)
    stack = [(source, None)]
    visited = set()
    parent_map = {}
    explored_count = 0
    target_found = False

    # 4. Depth Traversal Loop
    while stack:
        current, parent = stack.pop()

        if current in visited:
            continue

        visited.add(current)
        parent_map[current] = parent
        explored_count += 1

        if current == target:
            target_found = True
            break

        neighbors = list(graph.neighbors(current) if not graph.is_directed() else graph.successors(current))

        # Push unvisited neighbors onto stack
        for neighbor in neighbors:
            if neighbor not in visited:
                stack.append((neighbor, current))

    t_elapsed = (time.perf_counter() - t_start) * 1000.0

    # 5. Check if Target was reached
    if not target_found or target not in parent_map:
        return PathResult(
            algorithm="DFS",
            route_found=False,
            path=[],
            total_distance_m=0.0,
            estimated_travel_time_s=0.0,
            explored_nodes_count=explored_count,
            execution_time_ms=round(t_elapsed, 3),
            weight_used="unweighted (depth exploration)",
            message=f"No viable driving road route exists between node {source} and node {target}."
        )

    # 6. Reconstruct complete node sequence and real road distance/travel time metrics
    path, dist_m, time_s = reconstruct_path_and_metrics(graph, parent_map, source, target, weight_attr="length")

    return PathResult(
        algorithm="DFS",
        route_found=True,
        path=path,
        total_distance_m=dist_m,
        estimated_travel_time_s=time_s,
        explored_nodes_count=explored_count,
        execution_time_ms=round(t_elapsed, 3),
        weight_used="unweighted (depth exploration)",
        message="Route found using DFS (depth-first exploration; NOT optimized for distance or speed)."
    )

