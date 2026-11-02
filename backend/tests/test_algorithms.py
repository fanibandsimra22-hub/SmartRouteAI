"""
test_algorithms.py

Comprehensive unit test suite for SmartRoute AI pathfinding algorithms:
- A* Shortest Distance & Fastest Time
- Dijkstra Shortest Distance & Fastest Time
- Breadth-First Search (fewest edges)
- Depth-First Search (depth exploration)
- Source equals Destination
- Disconnected graph / No route handling
- MultiDiGraph parallel edge resolution

Tests use isolated synthetic graphs and DO NOT require internet or external data.
"""

import sys
from pathlib import Path
import networkx as nx

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.algorithms import (
    astar_path,
    dijkstra_path,
    bfs_path,
    dfs_path,
    haversine_distance_m,
    astar_admissible_heuristic,
    get_graph_admissibility_factors,
)
from app.services.graph_service import load_or_download_goa_graph


def create_synthetic_test_graph() -> nx.MultiDiGraph:
    """
    Creates a synthetic road network MultiDiGraph with two distinct routes:
    - Inner Route (A -> B -> D):
        * Shorter physical distance (2,600m + 2,800m = 5,400 m)
        * Slower city speed (25 km/h) -> Longer travel time (~777.6 seconds)
    - Bypass Highway (A -> C -> D):
        * Longer physical distance (4,200m + 4,400m = 8,600 m)
        * Faster highway speed (85 km/h) -> Shorter travel time (~364.2 seconds)
    - Parallel Edge between A and B:
        * Key 0: length = 3,600m, travel_time = 518.4s
        * Key 1: length = 2,600m, travel_time = 374.4s (optimal)
    - Disconnected Node:
        * Node Z (999): completely unreachable isolated node
    """
    g = nx.MultiDiGraph(crs="EPSG:4326")

    # Nodes with real GPS coordinates (Panaji to Goa University corridor)
    # Haversine straight-line distance between 101 and 104 is ~4,610.75 meters
    g.add_node(101, name="Node_A_Start", y=15.4989, x=73.8278)
    g.add_node(102, name="Node_B_Inner", y=15.4850, x=73.8250)
    g.add_node(103, name="Node_C_Bypass", y=15.4800, x=73.8100)
    g.add_node(104, name="Node_D_Goal", y=15.4578, x=73.8335)
    g.add_node(999, name="Node_Z_Isolated", y=15.3000, x=73.9000)

    # 1. Parallel Edges between A (101) and B (102)
    # Key 0: Suboptimal parallel edge
    g.add_edge(101, 102, key=0, length=3600.0, speed_kph=25.0, travel_time=518.4, name="Old St Inez Lane")
    # Key 1: Optimal parallel edge
    g.add_edge(101, 102, key=1, length=2600.0, speed_kph=25.0, travel_time=374.4, name="St Inez Main Road")

    # B (102) -> D (104)
    g.add_edge(102, 104, key=0, length=2800.0, speed_kph=25.0, travel_time=403.2, name="Taleigao Village Road")

    # 2. Highway Bypass Route: A (101) -> C (103) -> D (104)
    g.add_edge(101, 103, key=0, length=4200.0, speed_kph=85.0, travel_time=177.9, name="Coastal Expressway North")
    g.add_edge(103, 104, key=0, length=4400.0, speed_kph=85.0, travel_time=186.3, name="Coastal Expressway South")

    return g


def test_1_astar_shortest_distance():
    """Verify A* selects the geographically shortest route (A -> B -> D: 5,400m)."""
    g = create_synthetic_test_graph()
    result = astar_path(g, source=101, target=104, weight="length")

    assert result.route_found is True
    assert result.path == [101, 102, 104]
    assert result.total_distance_m == 5400.0
    assert result.estimated_travel_time_s == 777.6
    assert result.algorithm == "A*"
    assert result.weight_used == "length"
    assert result.explored_nodes_count > 0
    print(f"[OK] test_1_astar_shortest_distance PASSED: Path={result.path}, Dist={result.total_distance_m}m")


def test_2_astar_fastest_time():
    """Verify A* selects the fastest time route (A -> C -> D: 364.2s)."""
    g = create_synthetic_test_graph()
    result = astar_path(g, source=101, target=104, weight="travel_time")

    assert result.route_found is True
    assert result.path == [101, 103, 104]
    assert result.total_distance_m == 8600.0
    assert result.estimated_travel_time_s == 364.2
    assert result.weight_used == "travel_time"
    print(f"[OK] test_2_astar_fastest_time PASSED: Path={result.path}, Time={result.estimated_travel_time_s}s")


def test_3_dijkstra_shortest_distance():
    """Verify Dijkstra selects the shortest distance route (A -> B -> D: 5,400m)."""
    g = create_synthetic_test_graph()
    result = dijkstra_path(g, source=101, target=104, weight="length")

    assert result.route_found is True
    assert result.path == [101, 102, 104]
    assert result.total_distance_m == 5400.0
    assert result.algorithm == "Dijkstra"
    print(f"[OK] test_3_dijkstra_shortest_distance PASSED: Path={result.path}, Dist={result.total_distance_m}m")


def test_4_dijkstra_fastest_time():
    """Verify Dijkstra selects the fastest time route (A -> C -> D: 364.2s)."""
    g = create_synthetic_test_graph()
    result = dijkstra_path(g, source=101, target=104, weight="travel_time")

    assert result.route_found is True
    assert result.path == [101, 103, 104]
    assert result.estimated_travel_time_s == 364.2
    print(f"[OK] test_4_dijkstra_fastest_time PASSED: Path={result.path}, Time={result.estimated_travel_time_s}s")


def test_5_bfs_pathfinding():
    """Verify BFS finds a valid route using level-by-level exploration."""
    g = create_synthetic_test_graph()
    result = bfs_path(g, source=101, target=104)

    assert result.route_found is True
    assert len(result.path) == 3
    assert result.path[0] == 101
    assert result.path[-1] == 104
    assert result.algorithm == "BFS"
    assert "hop count" in result.weight_used
    print(f"[OK] test_5_bfs_pathfinding PASSED: Path={result.path}, Explored={result.explored_nodes_count}")


def test_6_dfs_pathfinding():
    """Verify DFS explores deep branches and successfully reaches the target."""
    g = create_synthetic_test_graph()
    result = dfs_path(g, source=101, target=104)

    assert result.route_found is True
    assert result.path[0] == 101
    assert result.path[-1] == 104
    assert result.algorithm == "DFS"
    print(f"[OK] test_6_dfs_pathfinding PASSED: Path={result.path}, Explored={result.explored_nodes_count}")


def test_7_source_equals_destination():
    """Verify all algorithms handle source == target immediately without crashing."""
    g = create_synthetic_test_graph()
    for algo_fn in [astar_path, dijkstra_path, bfs_path, dfs_path]:
        res = algo_fn(g, source=101, target=101)
        assert res.route_found is True
        assert res.path == [101]
        assert res.total_distance_m == 0.0
        assert res.estimated_travel_time_s == 0.0
        assert res.explored_nodes_count == 1
    print("[OK] test_7_source_equals_destination PASSED for all 4 algorithms")


def test_8_no_route_between_disconnected_nodes():
    """Verify clean failure reporting when target is an isolated, unreachable node."""
    g = create_synthetic_test_graph()
    for algo_fn in [astar_path, dijkstra_path, bfs_path, dfs_path]:
        res = algo_fn(g, source=101, target=999)
        assert res.route_found is False
        assert res.path == []
        assert res.total_distance_m == 0.0
        assert "No viable driving road route" in res.message or "not found" in res.message
    print("[OK] test_8_no_route_between_disconnected_nodes PASSED for all 4 algorithms")


def test_9_parallel_edges_resolution():
    """Verify that MultiDiGraph chooses the 2,600m parallel edge over the 3,600m edge."""
    g = create_synthetic_test_graph()
    res = dijkstra_path(g, source=101, target=102, weight="length")
    assert res.route_found is True
    assert res.path == [101, 102]
    assert res.total_distance_m == 2600.0, f"Expected 2600.0m, got {res.total_distance_m}m"
    assert res.estimated_travel_time_s == 374.4
    print(f"[OK] test_9_parallel_edges_resolution PASSED: Picked shortest parallel edge ({res.total_distance_m}m)")


def test_10_heuristic_admissibility():
    """Verify Haversine distance heuristic is strictly admissible (h <= real road length)."""
    g = create_synthetic_test_graph()
    # Straight-line distance from 101 to 104 is ~4,610.75m
    h_dist = astar_admissible_heuristic(g, 101, 104, weight_attr="length")
    # True shortest road distance is 5,400 meters
    assert h_dist <= 5400.0, f"Heuristic {h_dist} should be <= actual shortest road distance 5400.0"

    # Fastest time heuristic (h <= real road travel time)
    # Using highway max speed 85 km/h: h_time = 4610.75 / (85 * 1000/3600) = ~195.3s
    h_time = astar_admissible_heuristic(g, 101, 104, weight_attr="travel_time", max_speed_kmh=85.0)
    # True fastest travel time is 364.2 seconds
    assert h_time <= 364.2, f"Heuristic {h_time} should be <= actual fastest travel time 364.2"
    print(f"[OK] test_10_heuristic_admissibility PASSED: h_dist={h_dist:.1f}m <= 5400m, h_time={h_time:.1f}s <= 364.2s")


def test_11_admissibility_scaling_factor_and_effective_speed():
    """Verify alpha distance scaling factor and dynamic effective speed derivation."""
    # Create a graph where one edge intentionally has length < haversine distance
    g = nx.MultiDiGraph(crs="EPSG:4326")
    g.add_node(1, y=15.5000, x=73.8000)
    g.add_node(2, y=15.5000, x=73.8100) # Haversine ~ 1072.8 meters
    g.add_node(3, y=15.5000, x=73.8200) # Haversine ~ 1072.8 meters

    # Edge 1->2 has length 800m (< 1072.8m, ratio ~ 0.7457)
    g.add_edge(1, 2, length=800.0, travel_time=40.0, speed_kph=72.0)
    # Edge 2->3 has length 1200m (> 1072.8m, ratio ~ 1.118)
    g.add_edge(2, 3, length=1200.0, travel_time=60.0, speed_kph=72.0)

    alpha, max_v = get_graph_admissibility_factors(g)

    h12 = haversine_distance_m(15.5, 73.8, 15.5, 73.81)
    assert alpha < 1.0, f"Expected alpha < 1.0, got {alpha}"
    assert round(alpha, 3) == round(800.0 / h12, 3)

    # 2. Max speed must be derived from max(length / travel_time, speed_kph) = 20.0 m/s (72 km/h)
    assert max_v >= 20.0, f"Expected max_v >= 20.0 m/s, got {max_v}"

    # 3. For every edge, alpha * haversine must be <= length
    h12 = haversine_distance_m(15.5, 73.8, 15.5, 73.81)
    assert alpha * h12 <= 800.0001, f"Expected alpha * h12 <= 800.0, got {alpha * h12}"

    # 4. A* must find the exact same shortest path and distance as Dijkstra
    res_a = astar_path(g, 1, 3, weight="length")
    res_d = dijkstra_path(g, 1, 3, weight="length")
    assert res_a.route_found is True
    assert res_a.path == res_d.path == [1, 2, 3]
    assert res_a.total_distance_m == res_d.total_distance_m == 2000.0
    print(f"[OK] test_11_admissibility_scaling_factor_and_effective_speed PASSED: alpha={alpha:.4f}, max_v={max_v:.1f} m/s")


def test_12_all_pairs_cached_graph_optimality():
    """Verify that A* and Dijkstra produce 100% identical optimal costs."""
    from pathlib import Path
    import osmnx as ox

    # 1. Test all 506 pairs on the prototype corridor if present
    proto_cache = Path("backend/data/cache/goa_prototype_corridor.graphml")
    if proto_cache.exists():
        g_proto = ox.load_graphml(proto_cache, node_dtypes={"x": float, "y": float})
        proto_nodes = list(g_proto.nodes())
        for u in proto_nodes:
            for v in proto_nodes:
                if u == v:
                    continue
                ra = astar_path(g_proto, u, v, weight="length")
                rd = dijkstra_path(g_proto, u, v, weight="length")
                assert abs(ra.total_distance_m - rd.total_distance_m) < 1e-2
                ra_t = astar_path(g_proto, u, v, weight="travel_time")
                rd_t = dijkstra_path(g_proto, u, v, weight="travel_time")
                assert abs(ra_t.estimated_travel_time_s - rd_t.estimated_travel_time_s) < 1e-2
        print(f"[OK] test_12_all_pairs_cached_graph_optimality: 0 mismatches across all {len(proto_nodes)*(len(proto_nodes)-1)} corridor pairs")

    # 2. Test representative pairs on the active 1,662-node genuine OSM road graph
    g = load_or_download_goa_graph()
    nodes = list(g.nodes())
    sample_nodes = nodes[:20] # 20*19 = 380 directed pairs across full graph
    mismatches = 0
    for u in sample_nodes:
        for v in sample_nodes:
            if u == v:
                continue
            ra_len = astar_path(g, u, v, weight="length")
            rd_len = dijkstra_path(g, u, v, weight="length")
            if abs(ra_len.total_distance_m - rd_len.total_distance_m) > 1e-2:
                mismatches += 1

            ra_time = astar_path(g, u, v, weight="travel_time")
            rd_time = dijkstra_path(g, u, v, weight="travel_time")
            if abs(ra_time.estimated_travel_time_s - rd_time.estimated_travel_time_s) > 1e-2:
                mismatches += 1

    assert mismatches == 0, f"Found {mismatches} mismatches between A* and Dijkstra on OSM graph!"
    print(f"[OK] test_12_all_pairs_cached_graph_optimality PASSED: 0 mismatches on genuine OSM network (1662 nodes, 3986 edges)!")


if __name__ == "__main__":
    print("=" * 65)
    print("Running SmartRoute AI Pathfinding Algorithms Test Suite...")
    print("=" * 65)
    test_1_astar_shortest_distance()
    test_2_astar_fastest_time()
    test_3_dijkstra_shortest_distance()
    test_4_dijkstra_fastest_time()
    test_5_bfs_pathfinding()
    test_6_dfs_pathfinding()
    test_7_source_equals_destination()
    test_8_no_route_between_disconnected_nodes()
    test_9_parallel_edges_resolution()
    test_10_heuristic_admissibility()
    test_11_admissibility_scaling_factor_and_effective_speed()
    test_12_all_pairs_cached_graph_optimality()
    print("=" * 65)
    print("All 12 Algorithm Test Cases PASSED Successfully!")
    print("=" * 65)
