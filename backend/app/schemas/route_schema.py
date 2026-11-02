"""
route_schema.py

Pydantic Validation Schemas for Route Calculation and Storage Endpoints
Validates coordinates, preferences, and API responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator

class CoordinatePair(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0)
    lng: float = Field(..., ge=-180.0, le=180.0)

class RouteCalculationRequest(BaseModel):
    origin_coords: List[float] = Field(..., description="[latitude, longitude] of starting point")
    destination_coords: List[float] = Field(..., description="[latitude, longitude] of destination")
    origin_name: Optional[str] = "Selected Origin"
    destination_name: Optional[str] = "Selected Destination"
    preference: str = Field(default="fastest", description="'fastest' | 'shortest'")

    @field_validator("origin_coords", "destination_coords")
    @classmethod
    def validate_coordinates(cls, v: List[float]) -> List[float]:
        if not isinstance(v, (list, tuple)) or len(v) != 2:
            raise ValueError("Coordinates must be an array of [latitude, longitude].")
        lat, lng = v[0], v[1]
        if not (-90.0 <= lat <= 90.0):
            raise ValueError(f"Latitude {lat} out of range [-90, 90].")
        if not (-180.0 <= lng <= 180.0):
            raise ValueError(f"Longitude {lng} out of range [-180, 180].")
        return [float(lat), float(lng)]

    @field_validator("preference")
    @classmethod
    def validate_preference(cls, v: str) -> str:
        clean = v.lower().strip()
        if clean not in ["fastest", "shortest"]:
            raise ValueError("Preference must be either 'fastest' or 'shortest'.")
        return clean

class WaypointStepSchema(BaseModel):
    id: int
    instruction: str
    distance: str
    time: str

class RouteDetailSchema(BaseModel):
    id: str
    preference: str
    preference_name: str
    badge: str
    distance_km: str
    numeric_distance_km: float
    estimated_time_min: int
    estimated_fuel_liters: str
    avg_speed_kmh: str
    route_color: str
    route_type: str # 'road_network' | 'simulated_corridor' | 'straight_line_preview'
    is_straight_line: bool = False
    is_simulated: bool = False
    traffic_level: str = "low"
    traffic_status_text: str = "Free flow"
    route_description: str
    algorithm_used: str = "A*"
    data_source: str = "OSM Road Network"
    origin_coords: List[float]
    destination_coords: List[float]
    path_coordinates: List[List[float]]
    itinerary_steps: List[WaypointStepSchema] = []

class RouteCalculationResponse(BaseModel):
    status: str = "success"
    active_preference: str
    route: RouteDetailSchema
    alternative_route: Optional[RouteDetailSchema] = None
    execution_time_ms: float

class SavedRouteCreate(BaseModel):
    origin_name: str
    origin_coords: List[float]
    destination_name: str
    destination_coords: List[float]
    preference: str = "fastest"
    distance_km: float
    estimated_time_min: int
