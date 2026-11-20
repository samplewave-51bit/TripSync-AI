"""
TripSync AI - Baseline Recommendation Models & Evaluation Pipeline
Evaluates and benchmarks multiple recommendation baselines against test splits:
1. Random Baseline (Uniform stochastic heuristic)
2. Global Mean Baseline (Unpersonalized central tendency)
3. Popularity / Bayes Prior Baseline (Non-personalized destination reputation)
4. Heuristic Interaction Weighted Rule (Zero-training domain weighting)
5. Pure NumPy Ridge Regressor (First-principles mathematical solver)
6. Scikit-Learn Ridge Regressor (Validated industrial benchmark)
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

from ml_pipeline.src.math_engine import NumpyRidgeRegressor, evaluate_ranking_across_groups

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("TripSyncBaseline")

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"
MODELS_DIR = BASE_DIR / "models"


class BaselineRecommenderEvaluator:
    """Orchestrates baseline model training, evaluation, and comparative benchmarking."""

    def __init__(self):
        self.feature_schema = self._load_schema()
        self.feature_cols = self.feature_schema["features"]
        self.target_col = self.feature_schema["target_variable"]

        logger.info(f"Loaded schema with {len(self.feature_cols)} features. Target: {self.target_col}")

        # Load Parquet splits
        self.train_df = pd.read_parquet(PROCESSED_DATA_DIR / "train_features.parquet")
        self.val_df = pd.read_parquet(PROCESSED_DATA_DIR / "val_features.parquet")
        self.test_df = pd.read_parquet(PROCESSED_DATA_DIR / "test_features.parquet")

        logger.info(
            f"Splits loaded - Train: {len(self.train_df):,}, Val: {len(self.val_df):,}, Test: {len(self.test_df):,}"
        )

        self.X_train = self.train_df[self.feature_cols].values
        self.y_train = self.train_df[self.target_col].values
        self.groups_train = self.train_df["persona_id"].values

        self.X_val = self.val_df[self.feature_cols].values
        self.y_val = self.val_df[self.target_col].values
        self.groups_val = self.val_df["persona_id"].values

        self.X_test = self.test_df[self.feature_cols].values
        self.y_test = self.test_df[self.target_col].values
        self.groups_test = self.test_df["persona_id"].values

    def _load_schema(self) -> Dict[str, Any]:
        schema_path = PROCESSED_DATA_DIR / "feature_schema.json"
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def evaluate_model_predictions(
        self,
        name: str,
        y_pred_val: np.ndarray,
        y_pred_test: np.ndarray,
        k_list: List[int] = [5, 10],
    ) -> Dict[str, Any]:
        """Calculates regression and ranking metrics for validation and test splits."""
        val_metrics = evaluate_ranking_across_groups(
            self.y_val, y_pred_val, self.groups_val, k_list=k_list
        )
        test_metrics = evaluate_ranking_across_groups(
            self.y_test, y_pred_test, self.groups_test, k_list=k_list
        )

        return {
            "model_name": name,
            "validation": val_metrics,
            "test": test_metrics,
        }

    def run_all_baselines(self) -> Dict[str, Any]:
        """Runs and evaluates all baseline recommendation models."""
        results = {}

        # 1. Random Baseline (Uniform Random in [1.0, 5.0])
        logger.info("Evaluating Model 1: Random Baseline...")
        np.random.seed(42)
        y_val_rand = np.random.uniform(1.0, 5.0, size=len(self.y_val))
        y_test_rand = np.random.uniform(1.0, 5.0, size=len(self.y_test))
        results["random_baseline"] = self.evaluate_model_predictions(
            "Random Baseline", y_val_rand, y_test_rand
        )

        # 2. Global Mean Baseline (Predict constant training mean)
        logger.info("Evaluating Model 2: Global Mean Baseline...")
        train_mean = float(np.mean(self.y_train))
        y_val_mean = np.full_like(self.y_val, train_mean)
        y_test_mean = np.full_like(self.y_test, train_mean)
        results["global_mean"] = self.evaluate_model_predictions(
            "Global Mean Baseline", y_val_mean, y_test_mean
        )

        # 3. Popularity / Bayes Prior Baseline (Non-personalized rating reputation)
        logger.info("Evaluating Model 3: Popularity Prior Baseline...")
        y_val_pop = self.val_df["bayes_rating_prior"].values
        y_test_pop = self.test_df["bayes_rating_prior"].values
        results["popularity_prior"] = self.evaluate_model_predictions(
            "Popularity Prior Baseline", y_val_pop, y_test_pop
        )

        # 4. Heuristic Interaction Weighted Rule (Domain heuristic without regression fitting)
        logger.info("Evaluating Model 4: Domain Heuristic Rule...")
        # 0.7 * cosine_affinity + 0.2 * budget_compat + 0.1 * normalized_prior -> scaled to [1.0, 5.0]
        y_val_heur = (
            0.65 * self.val_df["cosine_thematic_affinity"].values * 5.0
            + 0.20 * self.val_df["budget_compatibility"].values * 5.0
            + 0.10 * self.val_df["pacing_alignment"].values * 5.0
            + 0.05 * self.val_df["bayes_rating_prior"].values
        )
        y_test_heur = (
            0.65 * self.test_df["cosine_thematic_affinity"].values * 5.0
            + 0.20 * self.test_df["budget_compatibility"].values * 5.0
            + 0.10 * self.test_df["pacing_alignment"].values * 5.0
            + 0.05 * self.test_df["bayes_rating_prior"].values
        )
        results["heuristic_interaction"] = self.evaluate_model_predictions(
            "Heuristic Interaction Rule", y_val_heur, y_test_heur
        )

        # 5. Pure NumPy Ridge Regressor (From Scratch)
        logger.info("Fitting and evaluating Model 5: Pure NumPy Ridge Regressor...")
        numpy_ridge = NumpyRidgeRegressor(alpha=1.0)
        numpy_ridge.fit(self.X_train, self.y_train)
        y_val_npridge = numpy_ridge.predict(self.X_val)
        y_test_npridge = numpy_ridge.predict(self.X_test)
        results["numpy_ridge"] = self.evaluate_model_predictions(
            "Pure NumPy Ridge Regressor", y_val_npridge, y_test_npridge
        )

        # 6. Scikit-Learn Ridge Regressor (Benchmark)
        logger.info("Fitting and evaluating Model 6: Scikit-Learn Ridge Regressor...")
        sk_ridge = Ridge(alpha=1.0)
        sk_ridge.fit(self.X_train, self.y_train)
        y_val_skridge = sk_ridge.predict(self.X_val)
        y_test_skridge = sk_ridge.predict(self.X_test)
        results["sklearn_ridge"] = self.evaluate_model_predictions(
            "Scikit-Learn Ridge Regressor", y_val_skridge, y_test_skridge
        )

        # Numerical Equivalence Verification
        max_diff = float(np.max(np.abs(y_test_npridge - y_test_skridge)))
        weight_diff = float(np.max(np.abs(numpy_ridge.weights - sk_ridge.coef_)))
        bias_diff = float(np.abs(numpy_ridge.bias - sk_ridge.intercept_))
        logger.info(
            f"Equivalence Verification: Max Prediction Diff={max_diff:.2e}, "
            f"Weight Diff={weight_diff:.2e}, Bias Diff={bias_diff:.2e}"
        )

        # Serialize trained Ridge model and metadata
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        model_payload = {
            "model_type": "RidgeRegression",
            "alpha": 1.0,
            "features": self.feature_cols,
            "weights": {col: float(w) for col, w in zip(self.feature_cols, sk_ridge.coef_)},
            "bias": float(sk_ridge.intercept_),
            "sklearn_model": sk_ridge,
            "numpy_model": numpy_ridge,
        }
        joblib.dump(model_payload, MODELS_DIR / "baseline_ridge.joblib")
        logger.info(f"Saved baseline model artifact to {MODELS_DIR / 'baseline_ridge.joblib'}")

        # Save metrics JSON
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report_data = {
            "models": results,
            "verification": {
                "max_prediction_diff": max_diff,
                "weight_diff": weight_diff,
                "bias_diff": bias_diff,
                "is_numerically_identical": bool(max_diff < 1e-6),
            },
            "top_learned_weights": sorted(
                model_payload["weights"].items(), key=lambda x: abs(x[1]), reverse=True
            ),
        }
        with open(REPORTS_DIR / "baseline_metrics.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)
        logger.info(f"Saved metrics report to {REPORTS_DIR / 'baseline_metrics.json'}")

        return report_data

    def print_comparison_table(self, report_data: Dict[str, Any]):
        """Prints a structured summary table comparing all evaluated baselines."""
        headers = ["Model", "Test RMSE", "Test MAE", "Test R²", "NDCG@5", "NDCG@10", "P@5", "P@10"]
        rows = []
        for key, info in report_data["models"].items():
            t = info["test"]
            rows.append(
                [
                    info["model_name"],
                    f"{t['rmse']:.4f}",
                    f"{t['mae']:.4f}",
                    f"{t['r2']:.4f}",
                    f"{t['ndcg_at_5']:.4f}",
                    f"{t['ndcg_at_10']:.4f}",
                    f"{t['precision_at_5']:.4f}",
                    f"{t['precision_at_10']:.4f}",
                ]
            )

        col_widths = [max(len(row[i]) for row in [headers] + rows) for i in range(len(headers))]
        divider = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"

        print("\n" + "=" * 90)
        print("TRIPSYNC AI — BASELINE RECOMMENDATION MODELS BENCHMARK REPORT (TEST SET)")
        print("=" * 90)
        print(divider)
        header_str = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
        print(header_str)
        print(divider)
        for r in rows:
            print("| " + " | ".join(val.ljust(col_widths[i]) for i, val in enumerate(r)) + " |")
        print(divider)
        print("\nTop Learned Linear Feature Weights:")
        for feat, wt in report_data["top_learned_weights"][:6]:
            print(f"  * {feat:<28}: {wt:+.4f}")
        print("=" * 90 + "\n")


def main():
    evaluator = BaselineRecommenderEvaluator()
    report = evaluator.run_all_baselines()
    evaluator.print_comparison_table(report)


if __name__ == "__main__":
    main()
