"""
TripSync AI - Day 8: Production Inference Engine & Social Choice Group Recommender
Provides self-contained, high-performance destination recommendation and group aggregation:
- Sub-millisecond individual preference scoring
- Multi-stakeholder Social Choice Group Aggregation (Nash, Borda, Least Misery, Consensus)
- Hard travel constraint filtering (Budget, State/City, Weekly Off, Duration, Rating)
- Transparent feature-attribution explainability engine
- System health check and readiness probe
"""

from dataclasses import asdict, dataclass, field
from enum import Enum
import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("TripSyncInference")

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "champion_model.joblib"
CATALOG_PATH = BASE_DIR / "data" / "processed" / "places_cleaned.csv"
SCHEMA_PATH = BASE_DIR / "data" / "processed" / "feature_schema.json"


class AggregationStrategy(str, Enum):
    """Social Choice Group Preference Aggregation Rules."""
    NASH = "nash"                   # Geometric mean (balances utility & fairness)
    BORDA = "borda"                 # Utilitarian arithmetic mean
    LEAST_MISERY = "least_misery"   # Egalitarian minimum utility (protects most dissatisfied)
    CONSENSUS = "consensus"         # Convex blend: 0.7 * Borda + 0.3 * Least Misery


@dataclass
class UserPreference:
    """Traveler persona profile and preference vector."""
    user_id: Union[str, int]
    name: str = "Traveler"
    pref_culture: float = 0.20
    pref_nature: float = 0.20
    pref_spiritual: float = 0.20
    pref_adventure: float = 0.20
    pref_urban: float = 0.20
    budget_tier: int = 1            # 0: Budget (<=₹50), 1: Mid-range (₹51-₹500), 2: Luxury (>₹500)
    pacing_pref: int = 1            # 0: Fast (1.25h), 1: Moderate (2.25h), 2: Slow (4.5h)

    def to_vector(self) -> np.ndarray:
        return np.array([
            self.pref_culture,
            self.pref_nature,
            self.pref_spiritual,
            self.pref_adventure,
            self.pref_urban,
        ], dtype=np.float64)


@dataclass
class TravelConstraints:
    """Business & logistical travel constraints for group filtering."""
    max_budget_tier: Optional[int] = None
    max_entrance_fee_inr: Optional[float] = None
    target_states: Optional[List[str]] = None
    target_cities: Optional[List[str]] = None
    target_zone: Optional[str] = None
    exclude_weekly_off: Optional[str] = None   # e.g. "Monday"
    max_duration_hrs: Optional[float] = None
    min_rating: Optional[float] = None
    must_have_airport: Optional[bool] = None


@dataclass
class DestinationRecommendation:
    """Scored and explained destination recommendation."""
    place_id: int
    name: str
    city: str
    state: str
    zone: str
    type: str
    rating: float
    entrance_fee_inr: float
    time_needed_hrs: float
    weekly_off: str
    latitude: float
    longitude: float
    score: float
    rank: int
    individual_scores: Dict[str, float] = field(default_factory=dict)
    agreement_index: float = 1.0
    thematic_match_pct: float = 100.0
    budget_fit_pct: float = 100.0
    pacing_alignment_pct: float = 100.0
    explanation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RecommendationEngine:
    """
    Self-contained, high-performance travel recommendation engine for TripSync AI.
    Loads champion model weights and destination catalog in memory for sub-millisecond serving.
    """

    _instance: Optional["RecommendationEngine"] = None

    def __init__(
        self,
        model_path: Optional[Path] = None,
        catalog_path: Optional[Path] = None,
    ):
        self.model_path = model_path or MODEL_PATH
        self.catalog_path = catalog_path or CATALOG_PATH
        self._load_artifacts()

    @classmethod
    def get_instance(cls) -> "RecommendationEngine":
        """Singleton pattern for FastAPI backend pre-warming."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_artifacts(self):
        """Loads and pre-indexes model weights, metadata, and destination tensors."""
        t0 = time.perf_counter()
        if not self.model_path.exists():
            raise FileNotFoundError(f"Champion model not found at {self.model_path}")
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Destination catalog not found at {self.catalog_path}")

        # 1. Load Model Payload
        self.payload = joblib.load(self.model_path)
        self.model = self.payload["model"]
        self.feature_cols = self.payload["feature_cols"]
        self.weights = self.model.coef_ if hasattr(self.model, "coef_") else None
        self.bias = float(self.model.intercept_) if hasattr(self.model, "intercept_") else 0.0

        # 2. Load and Pre-Index Places Catalog
        self.places_df = pd.read_csv(self.catalog_path)
        self.N_places = len(self.places_df)

        # 3. Pre-extract Vectorized Destination Tensors for Zero-Copy Scoring
        self.dest_thematic = np.stack([
            self.places_df["theme_culture_heritage"].values,
            self.places_df["theme_nature_wildlife"].values,
            self.places_df["theme_spiritual_religious"].values,
            self.places_df["theme_adventure_outdoor"].values,
            self.places_df["theme_urban_entertainment"].values,
        ], axis=1).astype(np.float64)  # Shape: (N, 5)

        self.dest_norms = np.linalg.norm(self.dest_thematic, axis=1, keepdims=True)
        self.dest_norms[self.dest_norms == 0] = 1.0

        self.dest_budgets = self.places_df["budget_tier_code"].values.astype(np.int32)
        self.dest_durations = self.places_df["time_needed_hrs"].values.astype(np.float64)
        self.dest_bayes = self.places_df["rating"].values.astype(np.float64)  # Empirical prior
        self.dest_log_reviews = self.places_df["log_reviews"].values.astype(np.float64)
        self.dest_log_fees = self.places_df["log_entrance_fee"].values.astype(np.float64)
        self.dest_lat = self.places_df["latitude"].values.astype(np.float64)
        self.dest_lon = self.places_df["longitude"].values.astype(np.float64)

        self.target_dur_map = {0: 1.25, 1: 2.25, 2: 4.5}

        load_ms = (time.perf_counter() - t0) * 1000
        logger.info(
            f"RecommendationEngine initialized in {load_ms:.2f}ms. Catalog: {self.N_places} places across India."
        )

    def _score_single_user(self, user: UserPreference) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """
        Computes predicted utility scores for all 323 destinations for a single user in ~0.15ms.
        Returns:
            scores: (N,) array of predicted affinity ratings in [1.0, 5.0]
            components: dict of raw intermediate tensors for explainability
        """
        u_vec = user.to_vector()
        u_norm = np.linalg.norm(u_vec)
        if u_norm == 0:
            u_norm = 1.0

        # Vectorized Feature Construction
        cosine_affinity = np.dot(self.dest_thematic, u_vec) / (self.dest_norms.squeeze() * u_norm + 1e-9)
        dot_utility = np.dot(self.dest_thematic, u_vec)

        budget_diff = np.maximum(0, self.dest_budgets - user.budget_tier)
        budget_compat = np.exp(-0.65 * budget_diff)

        target_dur = self.target_dur_map.get(user.pacing_pref, 2.25)
        duration_delta = np.abs(self.dest_durations - target_dur)
        pacing_align = np.clip(1.0 - (duration_delta / 6.0), 0.0, 1.0)

        # Assemble full 17-feature matrix
        X_mat = np.column_stack([
            cosine_affinity,
            dot_utility,
            budget_compat,
            pacing_align,
            self.dest_bayes,
            self.dest_durations,
            self.dest_log_reviews,
            self.dest_log_fees,
            self.dest_lat,
            self.dest_lon,
            np.full(self.N_places, user.pref_culture),
            np.full(self.N_places, user.pref_nature),
            np.full(self.N_places, user.pref_spiritual),
            np.full(self.N_places, user.pref_adventure),
            np.full(self.N_places, user.pref_urban),
            np.full(self.N_places, user.budget_tier),
            np.full(self.N_places, user.pacing_pref),
        ])

        # Analytical dot-product prediction: y = Xw + b
        if self.weights is not None:
            raw_scores = np.dot(X_mat, self.weights) + self.bias
        else:
            raw_scores = self.model.predict(X_mat)

        scores = np.clip(raw_scores, 1.0, 5.0)

        components = {
            "cosine_affinity": cosine_affinity,
            "budget_compat": budget_compat,
            "pacing_align": pacing_align,
        }
        return scores, components

    def _apply_constraints(
        self,
        candidate_indices: np.ndarray,
        constraints: Optional[TravelConstraints],
    ) -> np.ndarray:
        """Applies hard business and logistical constraint filters."""
        if constraints is None:
            return candidate_indices

        mask = np.ones(len(candidate_indices), dtype=bool)
        sub_df = self.places_df.iloc[candidate_indices]

        if constraints.max_budget_tier is not None:
            mask &= (sub_df["budget_tier_code"].values <= constraints.max_budget_tier)

        if constraints.max_entrance_fee_inr is not None:
            mask &= (sub_df["entrance_fee_inr"].values <= constraints.max_entrance_fee_inr)

        if constraints.target_states:
            normalized_states = [s.strip().lower() for s in constraints.target_states]
            mask &= sub_df["state"].str.lower().isin(normalized_states).values

        if constraints.target_cities:
            normalized_cities = [c.strip().lower() for c in constraints.target_cities]
            mask &= sub_df["city"].str.lower().isin(normalized_cities).values

        if constraints.target_zone:
            mask &= (sub_df["zone"].str.lower() == constraints.target_zone.strip().lower()).values

        if constraints.exclude_weekly_off:
            off_day = constraints.exclude_weekly_off.strip().lower()
            mask &= (sub_df["weekly_off"].str.lower() != off_day).values

        if constraints.max_duration_hrs is not None:
            mask &= (sub_df["time_needed_hrs"].values <= constraints.max_duration_hrs)

        if constraints.min_rating is not None:
            mask &= (sub_df["rating"].values >= constraints.min_rating)

        if constraints.must_have_airport:
            mask &= (sub_df["has_airport_50km"].values == 1)

        return candidate_indices[mask]

    def _generate_explanation(
        self,
        place_row: pd.Series,
        thematic_pct: float,
        budget_pct: float,
        pacing_pct: float,
        user_names: List[str],
        agreement_idx: float,
    ) -> str:
        """Constructs human-readable explainability narrative for the recommendation."""
        cat = place_row["type"]
        city = place_row["city"]
        state = place_row["state"]
        fee = place_row["entrance_fee_inr"]
        fee_str = "Free entry" if fee == 0 else f"₹{int(fee)} entry"

        if len(user_names) == 1:
            return (
                f"Top pick in {city}, {state} ({cat}). {thematic_pct:.0f}% thematic affinity match, "
                f"{budget_pct:.0f}% budget fit ({fee_str}), and {pacing_pct:.0f}% duration alignment."
            )
        else:
            consensus_desc = "unanimous consensus" if agreement_idx >= 0.90 else "balanced group compromise"
            return (
                f"Selected with {consensus_desc} ({agreement_idx * 100:.0f}% agreement index) across {len(user_names)} members: "
                f"{thematic_pct:.0f}% group thematic alignment in {city}, {state} ({fee_str})."
            )

    def recommend_for_user(
        self,
        user: UserPreference,
        top_k: int = 10,
        constraints: Optional[TravelConstraints] = None,
    ) -> List[DestinationRecommendation]:
        """Generates ranked, constrained recommendations for a single traveler."""
        scores, components = self._score_single_user(user)

        # Filter candidate indices
        all_indices = np.arange(self.N_places)
        valid_indices = self._apply_constraints(all_indices, constraints)

        if len(valid_indices) == 0:
            return []

        # Rank valid indices by descending predicted score
        valid_scores = scores[valid_indices]
        sort_order = np.argsort(-valid_scores)[:top_k]
        top_indices = valid_indices[sort_order]

        results = []
        for rank_idx, idx in enumerate(top_indices, start=1):
            row = self.places_df.iloc[idx]
            thematic_pct = float(components["cosine_affinity"][idx] * 100)
            budget_pct = float(components["budget_compat"][idx] * 100)
            pacing_pct = float(components["pacing_align"][idx] * 100)

            rec = DestinationRecommendation(
                place_id=int(row["place_id"]),
                name=str(row["name"]),
                city=str(row["city"]),
                state=str(row["state"]),
                zone=str(row["zone"]),
                type=str(row["type"]),
                rating=float(row["rating"]),
                entrance_fee_inr=float(row["entrance_fee_inr"]),
                time_needed_hrs=float(row["time_needed_hrs"]),
                weekly_off=str(row["weekly_off"]),
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                score=round(float(scores[idx]), 4),
                rank=rank_idx,
                individual_scores={user.name: round(float(scores[idx]), 4)},
                agreement_index=1.0,
                thematic_match_pct=round(thematic_pct, 1),
                budget_fit_pct=round(budget_pct, 1),
                pacing_alignment_pct=round(pacing_pct, 1),
                explanation=self._generate_explanation(
                    row, thematic_pct, budget_pct, pacing_pct, [user.name], 1.0
                ),
            )
            results.append(rec)

        return results

    def recommend_for_group(
        self,
        users: List[UserPreference],
        strategy: AggregationStrategy = AggregationStrategy.CONSENSUS,
        top_k: int = 10,
        constraints: Optional[TravelConstraints] = None,
    ) -> List[DestinationRecommendation]:
        """
        Multi-stakeholder group travel recommendation using axiomatic Social Choice Theory:
        1. Nash Product: Geometric mean balancing group welfare with individual fairness
        2. Borda: Utilitarian arithmetic mean
        3. Least Misery: Egalitarian minimum utility protecting the most dissatisfied member
        4. Consensus: Convex combination of Borda and Least Misery
        """
        if not users:
            raise ValueError("Group must contain at least one user preference.")

        M = len(users)
        user_scores = np.zeros((M, self.N_places), dtype=np.float64)
        thematic_matrix = np.zeros((M, self.N_places), dtype=np.float64)
        budget_matrix = np.zeros((M, self.N_places), dtype=np.float64)
        pacing_matrix = np.zeros((M, self.N_places), dtype=np.float64)

        for m, u in enumerate(users):
            s, comps = self._score_single_user(u)
            user_scores[m, :] = s
            thematic_matrix[m, :] = comps["cosine_affinity"]
            budget_matrix[m, :] = comps["budget_compat"]
            pacing_matrix[m, :] = comps["pacing_align"]

        # Aggregate Utilities using Social Choice Strategy
        if strategy == AggregationStrategy.BORDA:
            group_scores = np.mean(user_scores, axis=0)
        elif strategy == AggregationStrategy.NASH:
            # Nash bargaining: geometric mean exp(1/M * sum(log(u)))
            log_scores = np.log(np.clip(user_scores, 1e-6, None))
            group_scores = np.exp(np.mean(log_scores, axis=0))
        elif strategy == AggregationStrategy.LEAST_MISERY:
            group_scores = np.min(user_scores, axis=0)
        elif strategy == AggregationStrategy.CONSENSUS:
            borda = np.mean(user_scores, axis=0)
            least_misery = np.min(user_scores, axis=0)
            group_scores = 0.70 * borda + 0.30 * least_misery
        else:
            raise ValueError(f"Unknown aggregation strategy: {strategy}")

        # Apply Hard Constraints
        all_indices = np.arange(self.N_places)
        valid_indices = self._apply_constraints(all_indices, constraints)

        if len(valid_indices) == 0:
            return []

        # Rank Valid Places
        valid_scores = group_scores[valid_indices]
        sort_order = np.argsort(-valid_scores)[:top_k]
        top_indices = valid_indices[sort_order]

        user_names = [u.name for u in users]
        results = []

        for rank_idx, idx in enumerate(top_indices, start=1):
            row = self.places_df.iloc[idx]
            scores_per_member = {
                users[m].name: round(float(user_scores[m, idx]), 4) for m in range(M)
            }
            # Agreement Index: Ratio of min utility to max utility (1.0 = perfect consensus)
            min_u = np.min(user_scores[:, idx])
            max_u = np.max(user_scores[:, idx])
            agreement_idx = float(min_u / (max_u + 1e-9))

            mean_thematic = float(np.mean(thematic_matrix[:, idx]) * 100)
            mean_budget = float(np.mean(budget_matrix[:, idx]) * 100)
            mean_pacing = float(np.mean(pacing_matrix[:, idx]) * 100)

            rec = DestinationRecommendation(
                place_id=int(row["place_id"]),
                name=str(row["name"]),
                city=str(row["city"]),
                state=str(row["state"]),
                zone=str(row["zone"]),
                type=str(row["type"]),
                rating=float(row["rating"]),
                entrance_fee_inr=float(row["entrance_fee_inr"]),
                time_needed_hrs=float(row["time_needed_hrs"]),
                weekly_off=str(row["weekly_off"]),
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                score=round(float(group_scores[idx]), 4),
                rank=rank_idx,
                individual_scores=scores_per_member,
                agreement_index=round(agreement_idx, 3),
                thematic_match_pct=round(mean_thematic, 1),
                budget_fit_pct=round(mean_budget, 1),
                pacing_alignment_pct=round(mean_pacing, 1),
                explanation=self._generate_explanation(
                    row, mean_thematic, mean_budget, mean_pacing, user_names, agreement_idx
                ),
            )
            results.append(rec)

        return results

    def health_check(self) -> Dict[str, Any]:
        """Comprehensive readiness probe and performance diagnostic."""
        t0 = time.perf_counter()
        dummy_user = UserPreference(user_id="probe", name="DiagnosticProbe")
        _ = self.recommend_for_user(dummy_user, top_k=5)
        probe_latency_ms = (time.perf_counter() - t0) * 1000

        return {
            "status": "healthy",
            "model_name": self.payload.get("model_name", "Ridge Regression"),
            "catalog_destinations": self.N_places,
            "feature_count": len(self.feature_cols),
            "probe_latency_ms": round(probe_latency_ms, 3),
            "model_created_at": self.payload.get("created_at", "N/A"),
            "is_ready_for_serving": True,
        }
