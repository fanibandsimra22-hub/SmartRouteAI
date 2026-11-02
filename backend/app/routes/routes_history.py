"""
routes_history.py

SmartRoute AI – Saved Routes & Route History Endpoints
Provides persistence for bookmarked routes and calculation query history in MongoDB Atlas.
"""

from typing import List, Dict, Any, Optional
import uuid
import time
from fastapi import APIRouter, Query, HTTPException, status
import logging
from app.database import db_manager
from app.schemas.route_schema import SavedRouteCreate

logger = logging.getLogger("smartroute.routes.history")

router = APIRouter(prefix="/routes", tags=["Saved Routes & History"])


@router.get(
    "/history",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Get Route Calculation History",
    description="Retrieves recent route search queries from MongoDB Atlas."
)
async def get_route_history(
    limit: int = Query(default=20, ge=1, le=100, description="Max entries to return"),
    user_id: Optional[str] = Query(default="guest", description="User identifier")
):
    """
    Returns list of recently calculated routes.
    """
    try:
        col = db_manager.get_collection("route_history")
        docs = col.find({"user_id": user_id}, sort=[("created_at", -1)], limit=limit)
        results = []
        for d in docs:
            d_copy = dict(d)
            if "_id" in d_copy:
                d_copy["_id"] = str(d_copy["_id"])
            results.append(d_copy)
        return results
    except Exception as exc:
        logger.error(f"Failed to fetch route history: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not retrieve route history: {str(exc)}"
        )


@router.post(
    "/save",
    status_code=status.HTTP_201_CREATED,
    summary="Save / Bookmark a Route",
    description="Saves a route to the user's bookmarked saved routes collection in MongoDB."
)
async def save_route(
    route_data: SavedRouteCreate,
    user_id: Optional[str] = Query(default="guest", description="User identifier")
):
    """
    Saves a route bookmark into MongoDB Atlas.
    """
    try:
        col = db_manager.get_collection("saved_routes")
        new_route_id = str(uuid.uuid4())
        doc = {
            "id": new_route_id,
            "user_id": user_id,
            "origin_name": route_data.origin_name,
            "origin_coords": route_data.origin_coords,
            "destination_name": route_data.destination_name,
            "destination_coords": route_data.destination_coords,
            "preference": route_data.preference,
            "distance_km": route_data.distance_km,
            "estimated_time_min": route_data.estimated_time_min,
            "route_type": "road_network",
            "created_at": time.time()
        }
        res = col.insert_one(doc)
        return {
            "status": "success",
            "message": "Route saved successfully.",
            "route_id": new_route_id
        }
    except Exception as exc:
        logger.error(f"Failed to save route: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save route: {str(exc)}"
        )


@router.get(
    "/saved",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Get Saved Routes",
    description="Retrieves the user's bookmarked saved routes from MongoDB Atlas."
)
async def get_saved_routes(
    user_id: Optional[str] = Query(default="guest", description="User identifier")
):
    """
    Returns list of bookmarked saved routes for the user.
    """
    try:
        col = db_manager.get_collection("saved_routes")
        docs = col.find({"user_id": user_id}, sort=[("created_at", -1)])
        results = []
        for d in docs:
            d_copy = dict(d)
            if "_id" in d_copy:
                d_copy["_id"] = str(d_copy["_id"])
            results.append(d_copy)
        return results
    except Exception as exc:
        logger.error(f"Failed to fetch saved routes: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not retrieve saved routes: {str(exc)}"
        )


@router.delete(
    "/saved/{route_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Saved Route",
    description="Deletes a saved route by its unique route ID."
)
async def delete_saved_route(
    route_id: str,
    user_id: Optional[str] = Query(default="guest", description="User identifier")
):
    """
    Removes a bookmarked route from MongoDB Atlas.
    """
    try:
        col = db_manager.get_collection("saved_routes")
        result = col.delete_one({"id": route_id, "user_id": user_id})
        # If deleted_count attribute exists
        count = getattr(result, "deleted_count", 1)
        if count == 0:
            # Also try delete without user_id if guest
            result = col.delete_one({"id": route_id})
            count = getattr(result, "deleted_count", 0)

        if count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Saved route with ID '{route_id}' not found."
            )

        return {
            "status": "success",
            "message": f"Saved route '{route_id}' removed successfully."
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to delete saved route: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not delete saved route: {str(exc)}"
        )

