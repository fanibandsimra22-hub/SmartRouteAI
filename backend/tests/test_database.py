"""
test_database.py

Automated Test Suite for SmartRoute AI Database Operations
Tests:
- Database connectivity and index initialization
- Users collection operations
- Saved Routes collection CRUD
- Saved Locations collection CRUD
- Route History recording
- Health check integration returning database diagnostics
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
import uuid

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.database import db_manager, get_database
from app.models.user import UserModel
from app.models.route import SavedRouteModel, RouteHistoryModel
from app.models.saved_location import SavedLocationModel

client = TestClient(app)

def test_database_initialization():
    """Verify database manager initializes and exposes required collections."""
    db = get_database()
    assert db is not None, "Database instance should not be None"
    status = db_manager.get_status()
    assert "connected" in status
    assert "collections" in status
    assert "users" in status["collections"]
    assert "saved_routes" in status["collections"]
    assert "saved_locations" in status["collections"]
    assert "route_history" in status["collections"]
    print("[OK] test_database_initialization PASSED (Mode:", status["mode"], ")")

def test_users_collection_operations():
    """Verify user document creation, lookup, and deletion."""
    db = get_database()
    test_user_id = str(uuid.uuid4())
    test_email = f"test_{uuid.uuid4().hex[:6]}@smartroute.ai"

    user = UserModel(
        id=test_user_id,
        name="Engineer Tester",
        email=test_email,
        hashed_password="mock_hashed_secret_password_123"
    )

    # Insert
    result = db.users.insert_one(user.model_dump())
    assert result is not None

    # Find
    retrieved = db.users.find_one({"email": test_email})
    assert retrieved is not None
    assert retrieved["name"] == "Engineer Tester"
    assert retrieved["email"] == test_email
    assert retrieved["id"] == test_user_id

    # Clean up
    db.users.delete_one({"id": test_user_id})
    assert db.users.find_one({"id": test_user_id}) is None
    print("[OK] test_users_collection_operations PASSED")

def test_saved_routes_collection_operations():
    """Verify saving a route, listing by user_id, and deleting."""
    db = get_database()
    test_user_id = f"user_{uuid.uuid4().hex[:8]}"

    route = SavedRouteModel(
        user_id=test_user_id,
        origin_name="Panaji",
        origin_coords=[15.4989, 73.8278],
        destination_name="Goa University",
        destination_coords=[15.4578, 73.8335],
        preference="fastest",
        distance_km=7.4,
        estimated_time_min=16
    )

    db.saved_routes.insert_one(route.model_dump())

    # Query by user
    user_routes = list(db.saved_routes.find({"user_id": test_user_id}))
    assert len(user_routes) == 1
    assert user_routes[0]["origin_name"] == "Panaji"
    assert user_routes[0]["destination_name"] == "Goa University"
    assert user_routes[0]["distance_km"] == 7.4

    # Delete
    db.saved_routes.delete_one({"id": route.id})
    remaining = list(db.saved_routes.find({"user_id": test_user_id}))
    assert len(remaining) == 0
    print("[OK] test_saved_routes_collection_operations PASSED")

def test_saved_locations_collection_operations():
    """Verify saving a favorite location (e.g. Miramar Beach)."""
    db = get_database()
    test_user_id = f"user_{uuid.uuid4().hex[:8]}"

    loc = SavedLocationModel(
        user_id=test_user_id,
        name="Miramar Beach",
        address="Panaji Coastal Belt, Goa",
        coordinates=[15.4805, 73.8115],
        category="favorite"
    )

    db.saved_locations.insert_one(loc.model_dump())

    retrieved = db.saved_locations.find_one({"user_id": test_user_id, "name": "Miramar Beach"})
    assert retrieved is not None
    assert retrieved["coordinates"] == [15.4805, 73.8115]

    db.saved_locations.delete_one({"id": loc.id})
    print("[OK] test_saved_locations_collection_operations PASSED")

def test_route_history_operations():
    """Verify recording anonymous or guest route search queries."""
    db = get_database()
    history_entry = RouteHistoryModel(
        user_id="guest",
        origin_name="Panaji",
        origin_coords=[15.4989, 73.8278],
        destination_name="Goa University",
        destination_coords=[15.4578, 73.8335],
        preference="fastest",
        distance_km=7.4,
        estimated_time_min=16,
        algorithm_used="A*"
    )

    db.route_history.insert_one(history_entry.model_dump())
    retrieved = db.route_history.find_one({"id": history_entry.id})
    assert retrieved is not None
    assert retrieved["algorithm_used"] == "A*"
    assert retrieved["user_id"] == "guest"

    db.route_history.delete_one({"id": history_entry.id})
    print("[OK] test_route_history_operations PASSED")

def test_api_health_includes_database_diagnostics():
    """Verify GET /api/health returns database status diagnostics."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "database" in data
    db_info = data["database"]
    assert "collections" in db_info
    assert "users" in db_info["collections"]
    assert "saved_routes" in db_info["collections"]
    print("[OK] test_api_health_includes_database_diagnostics PASSED:", db_info)

if __name__ == "__main__":
    print("=" * 60)
    print("Running SmartRoute AI Phase 3 Database Test Suite...")
    print("=" * 60)
    test_database_initialization()
    test_users_collection_operations()
    test_saved_routes_collection_operations()
    test_saved_locations_collection_operations()
    test_route_history_operations()
    test_api_health_includes_database_diagnostics()
    print("=" * 60)
    print("All Phase 3 Database Tests Completed Successfully!")
    print("=" * 60)
