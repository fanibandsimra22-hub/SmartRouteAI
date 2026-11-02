"""
locations.py

SmartRoute AI – Location Search & Geocoding Endpoints
Handles location autocomplete and geocoding queries using OSM Nominatim and curated landmarks.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query, HTTPException, status
from app.services.geocoding_service import search_locations

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.get(
    "/search",
    response_model=List[Dict[str, Any]],
    summary="Search Locations in Goa",
    description="Searches for locations, landmarks, and addresses in Goa using cached Nominatim geocoding.",
    status_code=status.HTTP_200_OK
)
async def search_locations_endpoint(
    q: str = Query(..., min_length=2, description="Location search query (e.g. 'Panaji', 'Miramar', 'Goa University')"),
    limit: int = Query(default=8, ge=1, le=20, description="Maximum number of results to return")
):
    """
    Returns search results for a location query.
    """
    try:
        results = await search_locations(query=q, limit=limit)
        return results
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Location geocoding error: {str(exc)}"
        )

