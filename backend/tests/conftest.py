"""
Pytest configuration and test client fixtures for TripSync AI backend.
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture(scope="session")
def client():
    """Provides test HTTP client with active application lifespan."""
    with TestClient(app) as test_client:
        yield test_client
