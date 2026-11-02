"""
test_health.py

Integration Test for FastAPI Health Endpoint
Tests that the /api/health endpoint returns HTTP 200 with required diagnostic keys.
"""

import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_health_endpoint():
    """Verify GET /api/health returns 200 OK with operational status."""
    response = client.get("/api/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert data["status"] == "healthy", f"Expected healthy, got {data.get('status')}"
    assert "version" in data, "Missing version in health response"
    assert "timestamp" in data, "Missing timestamp in health response"
    assert "modules" in data, "Missing modules in health response"
    print("[OK] test_api_health_endpoint PASSED:", data)

def test_root_endpoint():
    """Verify GET / returns welcome payload and documentation links."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "/docs" in data["documentation"]
    print("[OK] test_root_endpoint PASSED:", data)

if __name__ == "__main__":
    print("Running SmartRoute AI Phase 2 Test Suite...")
    test_api_health_endpoint()
    test_root_endpoint()
    print("All Phase 2 tests passed successfully!")
