"""
algorithms package for SmartRoute AI.
Exports core pathfinding algorithms: A*, Dijkstra, BFS, and DFS,
along with shared result structures and geometric helpers.
"""

from app.algorithms.common import (
    PathResult,
    haversine_distance_m,
    astar_admissible_heuristic,
    get_graph_admissibility_factors,
    get_best_edge,
    reconstruct_path_and_metrics,
)
from app.algorithms.astar import astar_path
from app.algorithms.dijkstra import dijkstra_path
from app.algorithms.bfs import bfs_path
from app.algorithms.dfs import dfs_path

__all__ = [
    "PathResult",
    "astar_path",
    "dijkstra_path",
    "bfs_path",
    "dfs_path",
    "haversine_distance_m",
    "astar_admissible_heuristic",
    "get_graph_admissibility_factors",
    "get_best_edge",
    "reconstruct_path_and_metrics",
]

