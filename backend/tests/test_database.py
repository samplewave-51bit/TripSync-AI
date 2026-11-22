"""
TripSync AI - Database Models, Migrations & Seeding Unit Test Suite
Validates:
1. ORM table creation & declarative mappings
2. Complete catalog seeding (323 attractions, ~214 destinations)
3. Foreign key constraints & cascade delete behavior
4. CRUD repository lookups, filtering & searches
"""

import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.crud.crud_attraction import attraction, destination
from backend.app.crud.crud_user import user
from backend.app.db.seed import seed_destinations_and_attractions
from backend.app.models.base import Base
from backend.app.models.destination import Attraction, Destination
from backend.app.models.trip import Preference, Trip, TripMember
from backend.app.models.user import User


class TestDatabaseAndSeeding(unittest.TestCase):
    """Database models and seeding integration test suite."""

    @classmethod
    def setUpClass(cls):
        """Creates an in-memory SQLite database session for testing."""
        cls.engine = create_engine("sqlite:///:memory:", echo=False)
        cls.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
        Base.metadata.create_all(bind=cls.engine)

    def setUp(self):
        self.db = self.SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_01_seeding_catalog(self):
        """Validates that seeding populates all 323 Indian tourist attractions."""
        dest_seeded, attr_seeded = seed_destinations_and_attractions(self.db)
        self.assertEqual(attr_seeded, 323, "Must seed exactly 323 attractions from cleaned dataset")
        self.assertGreater(dest_seeded, 100, "Must seed regional destination city hubs")

        # Verify idempotency
        dest_2, attr_2 = seed_destinations_and_attractions(self.db)
        self.assertEqual(attr_2, 0, "Idempotent seed must skip existing attractions")

        # Verify total database count
        total_attractions = self.db.query(Attraction).count()
        self.assertEqual(total_attractions, 323)

    def test_02_attraction_crud_searches(self):
        """Validates attraction repository queries and filters."""
        # Query specific attraction by place_id
        india_gate = attraction.get_by_place_id(self.db, place_id=1)
        self.assertIsNotNone(india_gate)
        self.assertEqual(india_gate.name, "India Gate")
        self.assertEqual(india_gate.city.lower(), "delhi")

        # Filter by state
        rajasthan_places = attraction.search_attractions(self.db, state="Rajasthan", limit=50)
        self.assertGreater(len(rajasthan_places), 0)
        for p in rajasthan_places:
            self.assertEqual(p.state.lower(), "rajasthan")

        # Search by text query
        fort_results = attraction.search_attractions(self.db, query="Fort", limit=10)
        self.assertGreater(len(fort_results), 0)
        for p in fort_results:
            self.assertTrue("fort" in p.name.lower() or "fort" in p.type.lower())

        # Free attractions filter
        free_places = attraction.search_attractions(self.db, max_fee=0.0, limit=20)
        self.assertGreater(len(free_places), 0)
        for p in free_places:
            self.assertEqual(p.entrance_fee_inr, 0.0)

    def test_03_user_creation_and_trips(self):
        """Validates user creation, trip creation, and relational cascade deletes."""
        # Create user
        new_user = User(
            email="traveler@tripsync.ai",
            hashed_password="hashed_secure_password",
            full_name="Arjun Mehta",
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        self.assertIsNotNone(new_user.id)
        fetched_user = user.get_by_email(self.db, "traveler@tripsync.ai")
        self.assertIsNotNone(fetched_user)
        self.assertEqual(fetched_user.full_name, "Arjun Mehta")

        # Create trip
        new_trip = Trip(
            title="Golden Triangle Expedition",
            description="Touring Delhi, Agra, and Jaipur",
            created_by=new_user.id,
            invite_code="GOLDEN-2026",
            status="PLANNING",
        )
        self.db.add(new_trip)
        self.db.commit()
        self.db.refresh(new_trip)

        # Add member and preference
        member = TripMember(trip_id=new_trip.id, user_id=new_user.id, role="OWNER")
        pref = Preference(
            trip_id=new_trip.id,
            user_id=new_user.id,
            budget_max=15000.0,
            pace_preference="MODERATE",
            category_weights={"culture_heritage": 0.8, "adventure_outdoor": 0.4},
        )
        self.db.add_all([member, pref])
        self.db.commit()

        # Verify relationships
        self.assertEqual(len(new_trip.members), 1)
        self.assertEqual(len(new_trip.preferences), 1)
        self.assertEqual(new_trip.creator.email, "traveler@tripsync.ai")

        # Test Cascade Delete on Trip
        trip_id = new_trip.id
        self.db.delete(new_trip)
        self.db.commit()

        # Members and preferences should be cascade-deleted
        remaining_members = self.db.query(TripMember).filter(TripMember.trip_id == trip_id).count()
        remaining_prefs = self.db.query(Preference).filter(Preference.trip_id == trip_id).count()
        self.assertEqual(remaining_members, 0)
        self.assertEqual(remaining_prefs, 0)


if __name__ == "__main__":
    unittest.main()
