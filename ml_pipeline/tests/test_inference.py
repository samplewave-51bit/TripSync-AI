"""
TripSync AI - Day 8: Automated Inference Service Test Suite
Validates:
1. Engine health check & readiness probe
2. Single-user recommendation scoring & sorting
3. Multi-stakeholder group aggregation (Nash, Borda, Least Misery, Consensus)
4. Business constraint filtering (Budget, Fee, State, City, Weekly Off, Duration)
5. Explainability output completeness & agreement indices
6. Sub-10ms operational latency benchmark under group load
"""

import logging
import time
import unittest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestTripSyncInference")

from ml_pipeline.src.inference import (
    AggregationStrategy,
    RecommendationEngine,
    TravelConstraints,
    UserPreference,
)


class TestTripSyncInferenceEngine(unittest.TestCase):
    """Comprehensive test harness for the TripSync recommendation service."""

    @classmethod
    def setUpClass(cls):
        """Initializes singleton recommendation engine."""
        cls.engine = RecommendationEngine.get_instance()

    def test_01_health_check(self):
        """Validates system readiness probe and metadata."""
        health = self.engine.health_check()
        self.assertEqual(health["status"], "healthy")
        self.assertTrue(health["is_ready_for_serving"])
        self.assertEqual(health["catalog_destinations"], 323)
        self.assertGreaterEqual(health["feature_count"], 17)
        self.assertLess(health["probe_latency_ms"], 50.0)

    def test_02_single_user_recommendation(self):
        """Validates single traveler ranking, score bounds, and sorting."""
        user = UserPreference(
            user_id="user_nature_1",
            name="Aarav",
            pref_nature=0.85,
            pref_adventure=0.60,
            pref_culture=0.10,
            budget_tier=1,
            pacing_pref=1,
        )
        recs = self.engine.recommend_for_user(user, top_k=8)

        self.assertEqual(len(recs), 8)
        # Check monotonic score ordering
        scores = [r.score for r in recs]
        self.assertEqual(scores, sorted(scores, reverse=True))

        for r in recs:
            self.assertGreaterEqual(r.score, 1.0)
            self.assertLessEqual(r.score, 5.0)
            self.assertIn("Aarav", r.individual_scores)
            self.assertGreater(len(r.explanation), 10)
            self.assertGreaterEqual(r.thematic_match_pct, 0.0)

    def test_03_group_recommendation_strategies(self):
        """Validates multi-user Social Choice aggregation algorithms."""
        users = [
            UserPreference(user_id="u1", name="HeritageLover", pref_culture=0.90, pref_adventure=0.10),
            UserPreference(user_id="u2", name="SpiritualSeeker", pref_spiritual=0.90, pref_urban=0.10),
            UserPreference(user_id="u3", name="NatureExplorer", pref_nature=0.90, pref_culture=0.10),
        ]

        for strategy in [
            AggregationStrategy.BORDA,
            AggregationStrategy.NASH,
            AggregationStrategy.LEAST_MISERY,
            AggregationStrategy.CONSENSUS,
        ]:
            with self.subTest(strategy=strategy):
                recs = self.engine.recommend_for_group(users, strategy=strategy, top_k=5)
                self.assertEqual(len(recs), 5)
                # Verify monotonic ranking
                scores = [r.score for r in recs]
                self.assertEqual(scores, sorted(scores, reverse=True))

                for r in recs:
                    self.assertEqual(len(r.individual_scores), 3)
                    self.assertIn("HeritageLover", r.individual_scores)
                    self.assertIn("SpiritualSeeker", r.individual_scores)
                    self.assertIn("NatureExplorer", r.individual_scores)
                    self.assertGreaterEqual(r.agreement_index, 0.0)
                    self.assertLessEqual(r.agreement_index, 1.0)
                    self.assertIn("agreement index", r.explanation)

    def test_04_constraint_filtering_budget(self):
        """Validates hard budget constraints and zero-cost filters."""
        user = UserPreference(user_id="budget_user", name="Karan", budget_tier=0)

        # 1. Free entry constraint
        free_constraints = TravelConstraints(max_entrance_fee_inr=0.0)
        free_recs = self.engine.recommend_for_user(user, top_k=10, constraints=free_constraints)
        self.assertGreater(len(free_recs), 0)
        for r in free_recs:
            self.assertEqual(r.entrance_fee_inr, 0.0)

        # 2. Budget tier constraint (tier 0 <= ₹50)
        tier0_constraints = TravelConstraints(max_budget_tier=0)
        tier0_recs = self.engine.recommend_for_user(user, top_k=10, constraints=tier0_constraints)
        for r in tier0_recs:
            self.assertLessEqual(r.entrance_fee_inr, 50.0)

    def test_05_constraint_filtering_geographic(self):
        """Validates State, City, and Zone geographic filters."""
        user = UserPreference(user_id="geo_user", name="Priya")

        # State filter: Rajasthan
        state_constraints = TravelConstraints(target_states=["Rajasthan"])
        state_recs = self.engine.recommend_for_user(user, top_k=5, constraints=state_constraints)
        self.assertGreater(len(state_recs), 0)
        for r in state_recs:
            self.assertEqual(r.state.lower(), "rajasthan")

        # City filter: Jaipur
        city_constraints = TravelConstraints(target_cities=["Jaipur"])
        city_recs = self.engine.recommend_for_user(user, top_k=5, constraints=city_constraints)
        self.assertGreater(len(city_recs), 0)
        for r in city_recs:
            self.assertEqual(r.city.lower(), "jaipur")

    def test_06_constraint_filtering_weekly_off(self):
        """Validates exclusion of destinations closed on specific days."""
        user = UserPreference(user_id="timing_user", name="Vikram")
        monday_off_constraint = TravelConstraints(exclude_weekly_off="Monday")
        recs = self.engine.recommend_for_user(user, top_k=15, constraints=monday_off_constraint)

        self.assertGreater(len(recs), 0)
        for r in recs:
            self.assertNotEqual(r.weekly_off.lower(), "monday")

    def test_07_constraint_filtering_duration(self):
        """Validates maximum duration constraint."""
        user = UserPreference(user_id="quick_user", name="Sneha")
        duration_constraint = TravelConstraints(max_duration_hrs=1.5)
        recs = self.engine.recommend_for_user(user, top_k=10, constraints=duration_constraint)

        self.assertGreater(len(recs), 0)
        for r in recs:
            self.assertLessEqual(r.time_needed_hrs, 1.5)

    def test_08_empty_constraint_fallback(self):
        """Validates safe empty return when impossible constraints are requested."""
        user = UserPreference(user_id="fallback_user", name="Dev")
        impossible_constraint = TravelConstraints(target_cities=["AtlantisNonExistentCity"])
        recs = self.engine.recommend_for_user(user, top_k=5, constraints=impossible_constraint)
        self.assertEqual(recs, [])

    def test_09_inference_latency_benchmark(self):
        """Verifies sub-10ms execution latency under multi-user group load."""
        group = [
            UserPreference(user_id=f"u_{i}", name=f"Member_{i}", pref_culture=0.2 * i)
            for i in range(1, 6)
        ]

        latencies = []
        for _ in range(50):
            t0 = time.perf_counter()
            _ = self.engine.recommend_for_group(
                group, strategy=AggregationStrategy.CONSENSUS, top_k=10
            )
            latencies.append((time.perf_counter() - t0) * 1000)

        median_latency = float(sorted(latencies)[len(latencies) // 2])
        p95_latency = float(sorted(latencies)[int(len(latencies) * 0.95)])

        logger.info(
            f"Latency Benchmark (5-member group): Median={median_latency:.2f}ms, p95={p95_latency:.2f}ms"
        )
        self.assertLess(median_latency, 10.0, "Median latency must be strictly under 10ms")
        self.assertLess(p95_latency, 20.0, "p95 latency must be strictly under 20ms")


if __name__ == "__main__":
    unittest.main()
