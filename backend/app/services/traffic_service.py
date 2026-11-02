"""
traffic_service.py

SmartRoute AI – Real-time Traffic Evaluation Service
Handles integration with TomTom Traffic API when credentials are provided in .env,
and provides graceful, transparent baseline fallback when credentials are absent or unreachable.

Strict Rules:
1. Never invent or synthesize fake live traffic conditions.
2. Label status strictly as LIVE, BASELINE, or UNAVAILABLE.
3. Keep all external API keys confidential on the backend.
"""

import logging
from typing import Dict, Any, Optional, List
import httpx
from app.config import settings

logger = logging.getLogger("smartroute.traffic_service")

# TomTom Traffic Flow Segment Data API Endpoint
TOMTOM_FLOW_ENDPOINT = "https://api.tomtom.com/traffic/services/4/flowSegmentData/relative0/10/json"

async def get_traffic_status_for_route(
    path_coordinates: List[List[float]],
    baseline_travel_time_sec: float
) -> Dict[str, Any]:
    """
    Evaluates real-time traffic for the route using TomTom Traffic API if configured.
    Samples key midpoints along the route coordinates.
    
    Returns:
        Dict[str, Any] with:
            - status: 'LIVE' | 'BASELINE' | 'UNAVAILABLE'
            - traffic_level: 'low' | 'moderate' | 'heavy'
            - traffic_status_text: Readable description
            - delay_seconds: Additional estimated delay
            - is_live: bool
    """
    api_key = settings.TOMTOM_API_KEY.strip() if settings.TOMTOM_API_KEY else ""

    # 1. Baseline Mode when no TomTom API Key is configured
    if not api_key:
        return {
            "status": "BASELINE",
            "traffic_level": "low",
            "traffic_status_text": "Baseline OSM speed estimates (TomTom API key not configured in .env)",
            "delay_seconds": 0,
            "delay_minutes": 0,
            "is_live": False,
            "provider": "OpenStreetMap Baseline"
        }

    # 2. Live Query if API key is present
    if not path_coordinates or len(path_coordinates) < 2:
        return {
            "status": "BASELINE",
            "traffic_level": "low",
            "traffic_status_text": "Insufficient coordinates for traffic sampling",
            "delay_seconds": 0,
            "delay_minutes": 0,
            "is_live": False,
            "provider": "OpenStreetMap Baseline"
        }

    try:
        # Sample midpoint of the path
        mid_idx = len(path_coordinates) // 2
        mid_point = path_coordinates[mid_idx]
        lat, lon = mid_point[0], mid_point[1]

        params = {
            "point": f"{lat},{lon}",
            "unit": "KMPH",
            "key": api_key
        }

        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(TOMTOM_FLOW_ENDPOINT, params=params)

            if response.status_code == 200:
                data = response.json()
                flow_data = data.get("flowSegmentData", {})
                current_speed = flow_data.get("currentSpeed", 0)
                free_flow_speed = flow_data.get("freeFlowSpeed", 0)
                current_travel_time = flow_data.get("currentTravelTime", 0)
                free_flow_travel_time = flow_data.get("freeFlowTravelTime", 0)

                delay_sec = max(0, current_travel_time - free_flow_travel_time)

                if free_flow_speed > 0:
                    speed_ratio = current_speed / free_flow_speed
                else:
                    speed_ratio = 1.0

                if speed_ratio >= 0.85:
                    traffic_level = "low"
                    status_desc = f"Live TomTom: Free flow ({current_speed} km/h, free-flow: {free_flow_speed} km/h)"
                elif speed_ratio >= 0.55:
                    traffic_level = "moderate"
                    status_desc = f"Live TomTom: Moderate congestion ({current_speed} km/h vs {free_flow_speed} km/h normal)"
                else:
                    traffic_level = "heavy"
                    status_desc = f"Live TomTom: Heavy congestion ({current_speed} km/h vs {free_flow_speed} km/h normal)"

                return {
                    "status": "LIVE",
                    "traffic_level": traffic_level,
                    "traffic_status_text": status_desc,
                    "delay_seconds": int(delay_sec),
                    "delay_minutes": round(delay_sec / 60.0, 1),
                    "is_live": True,
                    "provider": "TomTom Traffic API"
                }
            elif response.status_code in (401, 403):
                logger.warning(f"TomTom API authentication failed (HTTP {response.status_code}).")
                return {
                    "status": "UNAVAILABLE",
                    "traffic_level": "low",
                    "traffic_status_text": "TomTom API authentication rejected (Check TOMTOM_API_KEY). Showing baseline speeds.",
                    "delay_seconds": 0,
                    "delay_minutes": 0,
                    "is_live": False,
                    "provider": "OpenStreetMap Baseline"
                }
            else:
                logger.warning(f"TomTom API returned status {response.status_code}")
                return {
                    "status": "UNAVAILABLE",
                    "traffic_level": "low",
                    "traffic_status_text": f"TomTom API returned HTTP {response.status_code}. Showing baseline speeds.",
                    "delay_seconds": 0,
                    "delay_minutes": 0,
                    "is_live": False,
                    "provider": "OpenStreetMap Baseline"
                }

    except Exception as exc:
        logger.warning(f"TomTom live traffic lookup failed: {exc}. Falling back to baseline.")
        return {
            "status": "UNAVAILABLE",
            "traffic_level": "low",
            "traffic_status_text": f"Live traffic unreachable ({type(exc).__name__}). Showing baseline speeds.",
            "delay_seconds": 0,
            "delay_minutes": 0,
            "is_live": False,
            "provider": "OpenStreetMap Baseline"
        }

