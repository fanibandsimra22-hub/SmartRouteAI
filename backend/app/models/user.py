"""
user.py

MongoDB User Document Model
Represents registered user profiles with hashed passwords.
"""

from typing import Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field, EmailStr

class UserModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
