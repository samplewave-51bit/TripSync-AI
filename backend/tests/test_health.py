"""
Unit and integration tests for TripSync AI health, ping, and readiness endpoints.
"""

import unittest
from fastapi.testclient import TestClient

from backend.app.main import app


class TestHealthEndpoints(unittest.TestCase):
    """Test suite verifying backend operational probes."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_root_index(self):
        """Verifies root endpoint returns API links."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("project", data)
        self.assertIn("docs", data)
        self.assertIn("health", data)

    def test_ping_endpoint(self):
        """Verifies low-overhead ping response."""
        response = self.client.get("/api/v1/ping")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["ping"], "pong")
        self.assertIn("timestamp", data)

    def test_health_endpoint(self):
        """Verifies comprehensive health check returns database and ML engine status."""
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn(data["status"], ["healthy", "degraded"])
        self.assertIn("database", data)
        self.assertIn("ml_engine", data)
        self.assertTrue(data["database"]["is_healthy"])
        self.assertTrue(data["ml_engine"]["is_ready_for_serving"])
        self.assertEqual(data["ml_engine"]["catalog_destinations"], 323)

    def test_readiness_probe(self):
        """Verifies readiness probe returns 200 when ready."""
        response = self.client.get("/api/v1/ready")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["ready"])


if __name__ == "__main__":
    unittest.main()
