"""
route.py

MongoDB Document Models for Saved Routes and Route History
Represents saved bookmarks and query history entries.
"""

from typing import Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

class SavedRouteModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    origin_name: str
    origin_coords: List[float] # [lat, lng]
    destination_name: str
    destination_coords: List[float] # [lat, lng]
    preference: str = "fastest" # 'fastest' | 'shortest'
    distance_km: float
    estimated_time_min: int
    route_type: str = "road_network"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RouteHistoryModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = "guest"
    origin_name: str
    origin_coords: List[float]
    destination_name: str
    destination_coords: List[float]
    preference: str = "fastest"
    distance_km: float
    estimated_time_min: int
    algorithm_used: str = "A*"
    traffic_level: Optional[str] = "normal"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
