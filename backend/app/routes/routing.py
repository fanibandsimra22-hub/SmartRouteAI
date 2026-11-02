"""
routing.py

SmartRoute AI – Route Calculation Endpoints
Receives origin/destination coordinates and preference, runs pathfinding algorithms
across the real Goa road graph, and returns route geometry and turn-by-turn directions.
"""

from fastapi import APIRouter, Query, HTTPException, status
import logging
from app.schemas.route_schema import (
    RouteCalculationRequest,
    RouteCalculationResponse
)
from app.services.routing_service import compute_navigation_route

logger = logging.getLogger("smartroute.routes.routing")

router = APIRouter(tags=["Routing"])


@router.post(
    "/calculate-route",
    response_model=RouteCalculationResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate Optimal Road Route",
    description=(
        "Calculates real-world road navigation between origin and destination coordinates "
        "using A* (default) or benchmark algorithms (Dijkstra, BFS, DFS) across the Central Goa OSM network."
    )
)
async def calculate_route_endpoint(
    request: RouteCalculationRequest,
    algorithm: str = Query(
        default="astar",
        description="Pathfinding algorithm: 'astar' (default), 'dijkstra', 'bfs', 'dfs'"
    )
):
    """
    Computes road path, full curve geometry, travel time, distance, and turn-by-turn directions.
    """
    try:
        response = await compute_navigation_route(request=request, algorithm=algorithm)
        return response
    except ValueError as val_err:
        logger.warning(f"Route calculation rejected: {val_err}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err)
        )
    except Exception as exc:
        logger.error(f"Route calculation failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Route calculation failed: {str(exc)}"
        )

