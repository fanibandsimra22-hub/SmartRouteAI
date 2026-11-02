"""
saved_location.py

MongoDB Document Model for Saved Locations (Favorites)
Allows users to save frequent waypoints such as "Home", "Work", or "Goa University".
"""

from typing import Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

class SavedLocationModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str = Field(..., min_length=1, max_length=100)
    address: Optional[str] = None
    coordinates: List[float] # [latitude, longitude]
    category: Optional[str] = "custom" # 'home' | 'work' | 'favorite' | 'custom'
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
