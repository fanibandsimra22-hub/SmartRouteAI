"""
test_graph_service.py

Unit and integration tests for SmartRoute AI Road Network Graph Service.
Verifies:
1. Cache path resolution.
2. Graceful uninitialized stats handling.
3. Nearest node spatial resolution (vectorized Haversine).
4. Error handling with empty/invalid graphs.
5. Server startup isolation (graph is lazy-loaded, NOT downloaded at boot).
"""

import sys
from pathlib import Path
import networkx as nx

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.graph_service import (
    get_cache_path,
    get_graph_stats,
    get_nearest_node,
    clear_graph_cache,
    CENTRAL_GOA_BBOX,
    _find_nearest_node_vectorized,
)


def test_cache_path_resolution():
    """Verify default cache path is correctly resolved inside backend/data/cache/."""
    cache_path = get_cache_path()
    assert cache_path.name == "goa_central_roads.graphml"
    assert "data" in cache_path.parts
    assert "cache" in cache_path.parts
    print("[OK] test_cache_path_resolution PASSED:", cache_path)


def test_unloaded_graph_stats():
    """Verify stats returns clean uninitialized payload when no graph is loaded."""
    clear_graph_cache()
    stats = get_graph_stats()
    assert stats["status"] == "not_loaded"
    print("[OK] test_unloaded_graph_stats PASSED")


def test_nearest_node_resolution_on_mock_graph():
    """Verify nearest node spatial lookup finds the mathematically closest intersection."""
    # Create a small realistic Goa test MultiDiGraph with 3 landmarks:
    # Node 1: Panaji Church Square [15.4989, 73.8278]
    # Node 2: Miramar Beach [15.4805, 73.8115]
    # Node 3: Goa University [15.4578, 73.8335]
    g = nx.MultiDiGraph(crs="EPSG:4326")
    g.add_node(101, y=15.4989, x=73.8278, name="Panaji")
    g.add_node(102, y=15.4805, x=73.8115, name="Miramar")
    g.add_node(103, y=15.4578, x=73.8335, name="Goa University")

    # Add edges with length and speed
    g.add_edge(101, 102, length=2400.0, speed_kph=35.0, travel_time=246.8)
    g.add_edge(102, 103, length=3200.0, speed_kph=40.0, travel_time=288.0)

    # Test point right next to Panaji Church Square (15.4990, 73.8280)
    closest_to_panaji = get_nearest_node(g, lat=15.4990, lon=73.8280)
    assert closest_to_panaji == 101, f"Expected 101, got {closest_to_panaji}"

    # Test point close to Goa University (15.4570, 73.8330)
    closest_to_gu = get_nearest_node(g, lat=15.4570, lon=73.8330)
    assert closest_to_gu == 103, f"Expected 103, got {closest_to_gu}"

    # Test stats computation on this mock graph
    stats = get_graph_stats(g)
    assert stats["status"] == "loaded"
    assert stats["node_count"] == 3
    assert stats["edge_count"] == 2
    assert stats["total_road_length_km"] == 5.6
    assert stats["bounding_box"]["min_lat"] == 15.4578
    assert stats["bounding_box"]["max_lat"] == 15.4989

    print("[OK] test_nearest_node_resolution_on_mock_graph PASSED")


def test_empty_graph_error_handling():
    """Verify query against empty graph raises clean ValueError."""
    empty_g = nx.MultiDiGraph()
    try:
        get_nearest_node(empty_g, lat=15.4989, lon=73.8278)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Graph is empty" in str(e)
    print("[OK] test_empty_graph_error_handling PASSED")


def test_fastapi_server_import_does_not_download():
    """Verify that importing app.main does NOT trigger automatic graph download."""
    clear_graph_cache()
    from app.main import app
    from app.services.graph_service import _GLOBAL_ROAD_GRAPH
    # Graph must still be None because it must be lazily loaded
    assert _GLOBAL_ROAD_GRAPH is None, "Graph should NOT be loaded at app startup"
    print("[OK] test_fastapi_server_import_does_not_download PASSED")


if __name__ == "__main__":
    print("=" * 60)
    print("Running SmartRoute AI Graph Service Test Suite...")
    print("=" * 60)
    test_cache_path_resolution()
    test_unloaded_graph_stats()
    test_nearest_node_resolution_on_mock_graph()
    test_empty_graph_error_handling()
    test_fastapi_server_import_does_not_download()
    print("=" * 60)
    print("All Graph Service Tests PASSED Successfully!")
    print("=" * 60)
