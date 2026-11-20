"""
TripSync AI - Pure NumPy Mathematical Recommendation Engine
Implements closed-form Regularized Ridge Regression, Vectorized Affinity Scoring,
and Ranking Metrics (RMSE, MAE, NDCG@K, Precision@K) from scratch without ML libraries.
"""

from typing import Dict, List, Tuple
import numpy as np


class NumpyRidgeRegressor:
    """
    Pure NumPy implementation of L2-regularized Ordinary Least Squares (Ridge Regression).
    Mathematical Formulation:
        Cost Function: J(w, b) = 1/(2N) * ||Xw + b - y||_2^2 + (lambda / 2) * ||w||_2^2
        Closed-Form Analytical Solution:
            w* = (X_aug^T X_aug + lambda * I')^(-1) X_aug^T y
        where X_aug = [X, 1] includes the bias intercept column, and I' has 0 for the bias term.
    """

    def __init__(self, alpha: float = 1.0):
        self.alpha = float(alpha)
        self.weights = None
        self.bias = None
        self.is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray) -> "NumpyRidgeRegressor":
        """Fits weights analytically using closed-form normal equation."""
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)

        N, D = X.shape
        # Augment X with column of ones for the bias intercept term
        X_aug = np.hstack([X, np.ones((N, 1), dtype=np.float64)])

        # Construct regularization matrix (do not regularize the bias term)
        I_reg = np.eye(D + 1, dtype=np.float64)
        I_reg[-1, -1] = 0.0

        # Normal equation with numerical stabilization: (X^T X + alpha * I) w = X^T y
        A = np.dot(X_aug.T, X_aug) + self.alpha * I_reg
        b = np.dot(X_aug.T, y)

        # Solve linear system using Cholesky / LU decomposition
        w_aug = np.linalg.solve(A, b)

        self.weights = w_aug[:-1]
        self.bias = float(w_aug[-1])
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Computes predictions using matrix dot product: y_hat = Xw + b."""
        if not self.is_fitted:
            raise RuntimeError("Model is not fitted yet. Call fit() first.")
        X = np.asarray(X, dtype=np.float64)
        return np.dot(X, self.weights) + self.bias


class RecommendationMetrics:
    """
    Pure mathematical ranking and regression metrics implemented from first principles.
    """

    @staticmethod
    def root_mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """RMSE = sqrt(1/N * sum((y_i - y_hat_i)^2))"""
        diff = np.asarray(y_true) - np.asarray(y_pred)
        return float(np.sqrt(np.mean(diff ** 2)))

    @staticmethod
    def mean_absolute_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """MAE = 1/N * sum(|y_i - y_hat_i|)"""
        diff = np.abs(np.asarray(y_true) - np.asarray(y_pred))
        return float(np.mean(diff))

    @staticmethod
    def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """R^2 = 1 - (SS_res / SS_tot)"""
        y_true = np.asarray(y_true)
        ss_res = np.sum((y_true - np.asarray(y_pred)) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        if ss_tot == 0:
            return 1.0
        return float(1.0 - (ss_res / ss_tot))

    @staticmethod
    def dcg_at_k(relevance_scores: np.ndarray, k: int) -> float:
        """
        Discounted Cumulative Gain at rank K:
        DCG@K = sum_{i=1}^K (2^{rel_i} - 1) / log2(i + 1)
        """
        rel = np.asarray(relevance_scores)[:k]
        if len(rel) == 0:
            return 0.0
        gains = np.power(2.0, rel) - 1.0
        discounts = np.log2(np.arange(len(rel)) + 2.0)
        return float(np.sum(gains / discounts))

    @classmethod
    def ndcg_at_k(cls, y_true: np.ndarray, y_pred: np.ndarray, k: int = 5) -> float:
        """
        Normalized Discounted Cumulative Gain at rank K:
        NDCG@K = DCG@K / IDCG@K
        where IDCG@K is the Ideal DCG achieved by perfect ranking.
        """
        y_true = np.asarray(y_true)
        y_pred = np.asarray(y_pred)

        if len(y_true) == 0:
            return 0.0

        # Rank items by predicted scores
        pred_order = np.argsort(-y_pred)
        relevance_at_predicted = y_true[pred_order]
        actual_dcg = cls.dcg_at_k(relevance_at_predicted, k)

        # Ideal ranking order by ground-truth scores
        ideal_order = np.argsort(-y_true)
        relevance_at_ideal = y_true[ideal_order]
        ideal_dcg = cls.dcg_at_k(relevance_at_ideal, k)

        if ideal_dcg == 0:
            return 1.0 if actual_dcg == 0 else 0.0

        return float(actual_dcg / ideal_dcg)

    @staticmethod
    def precision_at_k(y_true: np.ndarray, y_pred: np.ndarray, k: int = 5, threshold: float = 4.0) -> float:
        """
        Precision@K: Fraction of top-K recommended items that are relevant (rating >= threshold).
        """
        pred_order = np.argsort(-np.asarray(y_pred))[:k]
        relevant_flags = np.asarray(y_true)[pred_order] >= threshold
        return float(np.mean(relevant_flags))


def evaluate_ranking_across_groups(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    group_ids: np.ndarray,
    k_list: List[int] = [5, 10],
) -> Dict[str, float]:
    """
    Computes average ranking metrics (Mean NDCG@K, Precision@K) partitioned by user group.
    """
    unique_groups = np.unique(group_ids)
    ndcg_scores = {k: [] for k in k_list}
    prec_scores = {k: [] for k in k_list}

    for g in unique_groups:
        mask = (group_ids == g)
        g_true = y_true[mask]
        g_pred = y_pred[mask]

        for k in k_list:
            ndcg_scores[k].append(RecommendationMetrics.ndcg_at_k(g_true, g_pred, k=k))
            prec_scores[k].append(RecommendationMetrics.precision_at_k(g_true, g_pred, k=k))

    metrics = {
        "rmse": RecommendationMetrics.root_mean_squared_error(y_true, y_pred),
        "mae": RecommendationMetrics.mean_absolute_error(y_true, y_pred),
        "r2": RecommendationMetrics.r2_score(y_true, y_pred),
    }
    for k in k_list:
        metrics[f"ndcg_at_{k}"] = float(np.mean(ndcg_scores[k]))
        metrics[f"precision_at_{k}"] = float(np.mean(prec_scores[k]))

    return metrics
