"""
graph_service.py

SmartRoute AI – Road Network Graph Management Service
Uses OSMnx 2.1.1 and NetworkX 3.7 to ingest, cache, and manage the real-world
driving road network for the Goa navigation corridor.

Key Responsibilities:
1. Download OpenStreetMap driving road network within the Central Goa urban boundary.
2. Cache the graph as a GraphML file inside backend/data/cache/ to avoid repeated downloads.
3. Reload the cached graph on subsequent runs in milliseconds.
4. Enrich edges with realistic speeds and travel times (in seconds).
5. Fast nearest-node spatial lookup for given GPS coordinates (latitude, longitude).
6. Comprehensive graph diagnostic statistics (nodes, edges, total road km, density).

================================================================================
GEOGRAPHICAL BOUNDARY EXPLANATION:
--------------------------------------------------------------------------------
The entire state of Goa spans ~3,700 km² and contains tens of thousands of rural
paths and tracks. Downloading the full state on each development machine is slow,
prone to Overpass API rate-limits, and creates a large memory footprint.

Instead, we target the "Greater Panaji & Central Goa Urban Corridor":
- West Longitude:  73.7800 (Miramar beach & Dona Paula coastal headland)
- South Latitude:  15.4300 (Goa University plateau & Bambolim / GMC complex)
- East Longitude:  73.9300 (Old Goa heritage zone & Kadamba bypass link)
- North Latitude:  15.5400 (Panaji city center, Mandovi bridges & Porvorim approach)

Bounding Box (OSMnx 2.1.1 format: west, south, east, north):
  bbox = (73.7800, 15.4300, 73.9300, 15.5400)

This area covers ~195 km² and encompasses the primary arterial routes:
- Dayanand Bandodkar Marg (Coastal Promenade)
- Dr. Jack de Sequeira Road (Miramar - Dona Paula link)
- St. Inez Road & Taleigao Main Road
- NH-66 Mandovi Bridge & Bambolim Bypass
- Ribandar Causeway & Old Goa Highway
================================================================================
"""

import os
import logging
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
import numpy as np
import networkx as nx
import osmnx as ox

# Configure module logger
logger = logging.getLogger("smartroute.graph_service")

# Resolve project directories
SERVICES_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SERVICES_DIR.parent.parent
DATA_DIR = BACKEND_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
DEFAULT_CACHE_FILE = CACHE_DIR / "goa_central_roads.graphml"

# Default Central Goa Bounding Box in OSMnx 2.1.1 format: (left, bottom, right, top) = (west, south, east, north)
CENTRAL_GOA_BBOX: Tuple[float, float, float, float] = (
    73.7800,  # west_lon
    15.4300,  # south_lat
    73.9300,  # east_lon
    15.5400   # north_lat
)

# Global in-memory singleton graph holder (lazy-loaded, NOT loaded at server boot)
_GLOBAL_ROAD_GRAPH: Optional[nx.MultiDiGraph] = None


def get_cache_path() -> Path:
    """Returns the absolute path to the default cached GraphML file."""
    return DEFAULT_CACHE_FILE


def load_or_download_goa_graph(
    cache_filepath: Optional[Path] = None,
    bbox: Optional[Tuple[float, float, float, float]] = None,
    force_download: bool = False
) -> nx.MultiDiGraph:
    """
    Loads the Goa driving road network from the local GraphML cache if present,
    or downloads it via OSMnx from OpenStreetMap and saves it to disk.

    Args:
        cache_filepath: Optional custom Path to save/load the GraphML file.
        bbox: Optional (west, south, east, north) bounding box tuple.
        force_download: If True, bypasses cache and re-downloads from OSM.

    Returns:
        nx.MultiDiGraph: The populated NetworkX road network graph.

    Raises:
        RuntimeError: If download fails and no valid cache file exists.
    """
    global _GLOBAL_ROAD_GRAPH

    target_cache = Path(cache_filepath) if cache_filepath else DEFAULT_CACHE_FILE
    target_bbox = bbox if bbox else CENTRAL_GOA_BBOX

    # Ensure target cache directory exists
    target_cache.parent.mkdir(parents=True, exist_ok=True)

    # 1. Attempt to load from local GraphML cache
    if target_cache.exists() and not force_download:
        try:
            logger.info(f"Loading cached road network graph from: {target_cache}")
            graph = ox.load_graphml(
                filepath=target_cache,
                node_dtypes={"x": float, "y": float}
            )
            logger.info(
                f"Successfully loaded cached graph: "
                f"{len(graph.nodes)} nodes, {len(graph.edges)} edges."
            )
            _GLOBAL_ROAD_GRAPH = graph
            return graph
        except Exception as err:
            logger.warning(
                f"Failed to load cached GraphML file ({target_cache}): {err}. "
                f"Will attempt fresh download."
            )

    # 2. Download road network from OpenStreetMap via OSMnx 2.1.1
    logger.info("=" * 60)
    logger.info("Downloading driving road network from OpenStreetMap via OSMnx...")
    logger.info(
        f"Bounding Box: West={target_bbox[0]}, South={target_bbox[1]}, "
        f"East={target_bbox[2]}, North={target_bbox[3]}"
    )
    logger.info("Network Type: 'drive' (motor vehicle accessible roads)")
    logger.info("=" * 60)

    try:
        # OSMnx 2.1.1 expects bbox=(west, south, east, north)
        graph = ox.graph_from_bbox(
            bbox=target_bbox,
            network_type="drive",
            simplify=True,
            retain_all=False  # Keep the largest connected road component
        )

        # Enrich graph with speed limits and travel times (in seconds)
        logger.info("Calculating edge travel speeds and travel times...")
        graph = ox.add_edge_speeds(graph, fallback=35.0)  # 35 km/h urban default
        graph = ox.add_edge_travel_times(graph)

        logger.info(
            f"Road network downloaded successfully: "
            f"{len(graph.nodes)} nodes, {len(graph.edges)} edges."
        )

        # 3. Save graph to cache
        try:
            logger.info(f"Saving graph to local cache at: {target_cache}")
            ox.save_graphml(graph, filepath=target_cache)
            logger.info("GraphML cache saved successfully.")
        except Exception as save_err:
            logger.warning(f"Could not write GraphML cache file: {save_err}")

        _GLOBAL_ROAD_GRAPH = graph
        return graph

    except Exception as download_err:
        logger.error(
            f"Failed to download road network from OpenStreetMap: {download_err}",
            exc_info=True
        )

        # If cache exists despite an error, attempt to load as emergency fallback
        if target_cache.exists():
            logger.info("Attempting emergency fallback load from existing cache...")
            try:
                graph = ox.load_graphml(filepath=target_cache)
                _GLOBAL_ROAD_GRAPH = graph
                return graph
            except Exception:
                pass

        raise RuntimeError(
            f"Could not initialize Goa road graph. Overpass download failed ({download_err}) "
            f"and no valid cache was available at {target_cache}."
        ) from download_err


def get_road_graph(auto_load: bool = True) -> Optional[nx.MultiDiGraph]:
    """
    Returns the loaded global road graph.

    Args:
        auto_load: If True and the graph is not yet in memory, triggers
                   loading from cache (or download if cache is missing).

    Returns:
        nx.MultiDiGraph or None: The active graph instance.
    """
    global _GLOBAL_ROAD_GRAPH
    if _GLOBAL_ROAD_GRAPH is None and auto_load:
        _GLOBAL_ROAD_GRAPH = load_or_download_goa_graph()
    return _GLOBAL_ROAD_GRAPH


def get_nearest_node(graph: nx.MultiDiGraph, lat: float, lon: float) -> int:
    """
    Finds the nearest road network node to a given GPS coordinate (latitude, longitude).

    Uses a fast vectorized Haversine search across node coordinates, with a graceful
    fallback to ox.nearest_nodes if available.

    Args:
        graph: NetworkX MultiDiGraph instance.
        lat: Target latitude in decimal degrees.
        lon: Target longitude in decimal degrees.

    Returns:
        int: The OSM node ID of the closest intersection/waypoint.

    Raises:
        ValueError: If the graph is empty or has no coordinates.
    """
    if graph is None or len(graph.nodes) == 0:
        raise ValueError("Cannot query nearest node: Graph is empty or None.")

    # 1. Try OSMnx built-in nearest_nodes first (X=lon, Y=lat)
    try:
        nearest = ox.nearest_nodes(graph, X=lon, Y=lat)
        return int(nearest)
    except (ImportError, Exception):
        # 2. Vectorized NumPy Haversine fallback (zero dependency on scikit-learn or scipy)
        return _find_nearest_node_vectorized(graph, lat, lon)


def _find_nearest_node_vectorized(graph: nx.MultiDiGraph, lat: float, lon: float) -> int:
    """
    Vectorized Haversine distance search across graph node coordinates.
    Executes in < 1 ms on graphs with thousands of nodes.
    """
    # Check if spatial node arrays are already cached on the graph object
    spatial_cache = graph.graph.get("_spatial_cache")
    if spatial_cache is None:
        node_ids: List[int] = []
        lats: List[float] = []
        lons: List[float] = []

        for node_id, data in graph.nodes(data=True):
            if "y" in data and "x" in data:
                node_ids.append(int(node_id))
                lats.append(float(data["y"]))
                lons.append(float(data["x"]))

        if not node_ids:
            raise ValueError("Graph nodes do not contain 'x' (lon) and 'y' (lat) attributes.")

        node_ids_arr = np.array(node_ids, dtype=np.int64)
        lats_rad = np.radians(np.array(lats, dtype=np.float64))
        lons_rad = np.radians(np.array(lons, dtype=np.float64))

        spatial_cache = {
            "node_ids": node_ids_arr,
            "lats_rad": lats_rad,
            "lons_rad": lons_rad,
        }
        graph.graph["_spatial_cache"] = spatial_cache

    node_ids_arr = spatial_cache["node_ids"]
    lats_rad = spatial_cache["lats_rad"]
    lons_rad = spatial_cache["lons_rad"]

    # Target point in radians
    target_lat_rad = np.radians(lat)
    target_lon_rad = np.radians(lon)

    # Great-circle distance using Haversine formula
    dlat = lats_rad - target_lat_rad
    dlon = lons_rad - target_lon_rad
    a = np.sin(dlat / 2.0) ** 2 + np.cos(target_lat_rad) * np.cos(lats_rad) * np.sin(dlon / 2.0) ** 2
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(np.maximum(0.0, 1.0 - a)))
    distances_m = 6371000.0 * c

    closest_idx = int(np.argmin(distances_m))
    return int(node_ids_arr[closest_idx])


def get_graph_stats(graph: Optional[nx.MultiDiGraph] = None) -> Dict[str, Any]:
    """
    Computes comprehensive structural and geographic statistics for the road graph.

    Args:
        graph: Optional MultiDiGraph. If None, uses the active global graph.

    Returns:
        Dict[str, Any]: Dictionary containing node count, edge count, total road km,
                        bounding box, and CRS information.
    """
    g = graph if graph is not None else _GLOBAL_ROAD_GRAPH
    if g is None:
        return {
            "status": "not_loaded",
            "message": "Graph is not currently loaded in memory."
        }

    total_length_m = 0.0
    speeds: List[float] = []

    for _, _, data in g.edges(data=True):
        total_length_m += float(data.get("length", 0.0))
        speed = data.get("speed_kph")
        if speed is not None:
            try:
                speeds.append(float(speed))
            except (ValueError, TypeError):
                pass

    avg_speed_kph = round(float(np.mean(speeds)), 1) if speeds else 35.0

    # Calculate actual node coordinate bounds
    lats = [d["y"] for _, d in g.nodes(data=True) if "y" in d]
    lons = [d["x"] for _, d in g.nodes(data=True) if "x" in d]

    bounds = None
    if lats and lons:
        bounds = {
            "min_lat": round(min(lats), 4),
            "max_lat": round(max(lats), 4),
            "min_lon": round(min(lons), 4),
            "max_lon": round(max(lons), 4),
        }

    return {
        "status": "loaded",
        "node_count": len(g.nodes),
        "edge_count": len(g.edges),
        "total_road_length_km": round(total_length_m / 1000.0, 2),
        "avg_speed_kph": avg_speed_kph,
        "is_directed": g.is_directed(),
        "is_multigraph": g.is_multigraph(),
        "crs": str(g.graph.get("crs", "EPSG:4326")),
        "bounding_box": bounds,
        "cache_file": str(DEFAULT_CACHE_FILE),
        "cache_exists": DEFAULT_CACHE_FILE.exists()
    }


def clear_graph_cache() -> None:
    """Clears the in-memory graph instance (useful for testing or cache reloading)."""
    global _GLOBAL_ROAD_GRAPH
    _GLOBAL_ROAD_GRAPH = None
    logger.info("In-memory road graph cleared.")

