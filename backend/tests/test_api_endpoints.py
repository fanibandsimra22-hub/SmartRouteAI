"""
test_api_endpoints.py

Comprehensive End-to-End API Integration Test Suite for SmartRoute AI
Tests all required endpoints:
- GET /api/health
- GET /api/locations/search
- POST /api/calculate-route (Fastest, Shortest, Dijkstra, BFS, DFS)
- GET /api/routes/history
- POST /api/routes/save
- GET /api/routes/saved
- DELETE /api/routes/saved/{route_id}
- Error handling for invalid inputs and edge cases
"""

import sys
import os
import unittest
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.main import app
from app.services.graph_service import load_or_download_goa_graph


class TestSmartRouteAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Preload road graph
        load_or_download_goa_graph()
        cls.client = TestClient(app)

    def test_01_health_endpoint(self):
        """Verify GET /api/health returns 200 and system diagnostics."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("database", data)
        self.assertIn("service", data)
        print("[OK] test_01_health_endpoint PASSED")

    def test_02_locations_search_endpoint(self):
        """Verify GET /api/locations/search returns matched landmarks."""
        response = self.client.get("/api/locations/search?q=Panaji&limit=5")
        self.assertEqual(response.status_code, 200)
        results = response.json()
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        first = results[0]
        self.assertIn("name", first)
        self.assertIn("lat", first)
        self.assertIn("lon", first)
        print(f"[OK] test_02_locations_search_endpoint PASSED: found {len(results)} matches for 'Panaji'")

    def test_03_calculate_route_fastest(self):
        """Verify POST /api/calculate-route returns A* fastest road route."""
        payload = {
            "origin_coords": [15.4989, 73.8278], # Panaji Church
            "destination_coords": [15.4578, 73.8335], # Goa University
            "origin_name": "Panaji Church Square",
            "destination_name": "Goa University",
            "preference": "fastest"
        }
        response = self.client.post("/api/calculate-route", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["active_preference"], "fastest")

        route = data["route"]
        self.assertFalse(route["is_straight_line"])
        self.assertFalse(route["is_simulated"])
        self.assertEqual(route["route_type"], "road_network")
        self.assertGreater(len(route["path_coordinates"]), 10)
        self.assertGreater(len(route["itinerary_steps"]), 2)
        self.assertGreater(route["numeric_distance_km"], 4.0)
        self.assertIn("traffic_status_text", route)
        print(f"[OK] test_03_calculate_route_fastest PASSED: {route['distance_km']}, {route['estimated_time_min']} mins, {len(route['path_coordinates'])} coords")

    def test_04_calculate_route_shortest(self):
        """Verify POST /api/calculate-route returns A* shortest road route."""
        payload = {
            "origin_coords": [15.4989, 73.8278],
            "destination_coords": [15.4578, 73.8335],
            "origin_name": "Panaji Church Square",
            "destination_name": "Goa University",
            "preference": "shortest"
        }
        response = self.client.post("/api/calculate-route", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["active_preference"], "shortest")
        self.assertIsNotNone(data["alternative_route"])
        print(f"[OK] test_04_calculate_route_shortest PASSED: {data['route']['distance_km']}")

    def test_05_calculate_route_dijkstra_benchmark(self):
        """Verify POST /api/calculate-route?algorithm=dijkstra works as benchmark."""
        payload = {
            "origin_coords": [15.4989, 73.8278],
            "destination_coords": [15.4578, 73.8335],
            "preference": "fastest"
        }
        response = self.client.post("/api/calculate-route?algorithm=dijkstra", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Dijkstra", data["route"]["algorithm_used"])
        print("[OK] test_05_calculate_route_dijkstra_benchmark PASSED")

    def test_06_calculate_route_bfs_dfs_academic_demo(self):
        """Verify academic BFS and DFS algorithms work via query parameter."""
        payload = {
            "origin_coords": [15.4989, 73.8278],
            "destination_coords": [15.4578, 73.8335],
            "preference": "shortest"
        }
        # Test BFS
        resp_bfs = self.client.post("/api/calculate-route?algorithm=bfs", json=payload)
        self.assertEqual(resp_bfs.status_code, 200)
        self.assertIn("BFS", resp_bfs.json()["route"]["algorithm_used"])

        # Test DFS
        resp_dfs = self.client.post("/api/calculate-route?algorithm=dfs", json=payload)
        self.assertEqual(resp_dfs.status_code, 200)
        self.assertIn("DFS", resp_dfs.json()["route"]["algorithm_used"])
        print("[OK] test_06_calculate_route_bfs_dfs_academic_demo PASSED")

    def test_07_route_history_lifecycle(self):
        """Verify GET /api/routes/history includes recently calculated queries."""
        response = self.client.get("/api/routes/history?limit=10")
        self.assertEqual(response.status_code, 200)
        history = response.json()
        self.assertIsInstance(history, list)
        self.assertGreater(len(history), 0)
        print(f"[OK] test_07_route_history_lifecycle PASSED: {len(history)} entries retrieved")

    def test_08_saved_routes_full_lifecycle(self):
        """Verify POST /api/routes/save, GET /api/routes/saved, and DELETE /api/routes/saved/{id}."""
        save_payload = {
            "origin_name": "Panaji Church Square",
            "origin_coords": [15.4989, 73.8278],
            "destination_name": "Goa University",
            "destination_coords": [15.4578, 73.8335],
            "preference": "fastest",
            "distance_km": 7.26,
            "estimated_time_min": 10
        }
        # 1. Save
        save_resp = self.client.post("/api/routes/save", json=save_payload)
        self.assertEqual(save_resp.status_code, 201)
        save_data = save_resp.json()
        route_id = save_data["route_id"]
        self.assertTrue(bool(route_id))

        # 2. Get saved list
        get_resp = self.client.get("/api/routes/saved")
        self.assertEqual(get_resp.status_code, 200)
        saved_list = get_resp.json()
        matching = [r for r in saved_list if r.get("id") == route_id]
        self.assertEqual(len(matching), 1)

        # 3. Delete
        del_resp = self.client.delete(f"/api/routes/saved/{route_id}")
        self.assertEqual(del_resp.status_code, 200)

        # 4. Verify deletion
        get_after = self.client.get("/api/routes/saved").json()
        remaining = [r for r in get_after if r.get("id") == route_id]
        self.assertEqual(len(remaining), 0)
        print(f"[OK] test_08_saved_routes_full_lifecycle PASSED (Saved -> Retrieved -> Deleted id: {route_id})")

    def test_09_invalid_coordinates_validation_error(self):
        """Verify 422 Unprocessable Entity for invalid latitude/longitude."""
        invalid_payload = {
            "origin_coords": [999.0, 73.8278], # Latitude 999 is invalid
            "destination_coords": [15.4578, 73.8335],
            "preference": "fastest"
        }
        response = self.client.post("/api/calculate-route", json=invalid_payload)
        self.assertEqual(response.status_code, 422)
        print("[OK] test_09_invalid_coordinates_validation_error PASSED: 422 rejected correctly")

    def test_10_missing_search_query_error(self):
        """Verify 422 Unprocessable Entity when location query is missing or too short."""
        response = self.client.get("/api/locations/search?q=a")
        self.assertEqual(response.status_code, 422)
        print("[OK] test_10_missing_search_query_error PASSED: 422 rejected correctly")


if __name__ == "__main__":
    print("=" * 65)
    print("Running SmartRoute AI Full API Integration Test Suite...")
    print("=" * 65)
    unittest.main(verbosity=2)

