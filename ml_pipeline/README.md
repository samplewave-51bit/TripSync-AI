# TripSync AI — Machine Learning Pipeline & Recommendation Engine

This module contains the end-to-end Machine Learning and Social Choice Intelligence pipeline for **TripSync AI**, powering hyper-personalized group travel recommendations across 323 iconic tourist destinations in India.

---

## 1. Architectural Overview

TripSync AI solves the group travel recommendation problem via a decoupled, two-stage mathematical framework:
1. **Stage 1 (Individual Utility Modeling):** Supervised regression predicting individual traveler affinity score $\hat{y}_{ui} \in [1.0, 5.0]$ based on multi-criteria interaction vectors (thematic cosine similarity, exponential budget decay, duration pacing alignment, and Bayesian reputation priors).
2. **Stage 2 (Axiomatic Social Choice Aggregation):** Blends individual preference scores across group members using formal Social Choice voting rules:
   - **Nash Product (Geometric Mean):** Maximizes collective welfare while penalizing extreme disparity:
     $$S_{nash}(i) = \left( \prod_{u \in U} \hat{y}_{ui} \right)^{1/|U|}$$
   - **Borda Count (Utilitarian Average):** Arithmetic consensus maximizing total group happiness:
     $$S_{borda}(i) = \frac{1}{|U|} \sum_{u \in U} \hat{y}_{ui}$$
   - **Least Misery (Egalitarian Fairness):** Prioritizes the most dissatisfied group member to prevent bad compromises:
     $$S_{least\_misery}(i) = \min_{u \in U} \hat{y}_{ui}$$
   - **Consensus (Convex Blend):** $0.70 \cdot S_{borda}(i) + 0.30 \cdot S_{least\_misery}(i)$.

---

## 2. Directory Layout

```
ml_pipeline/
├── data/
│   ├── raw/
│   │   └── top_indian_places.csv         # Raw Indian tourism destinations (325 rows)
│   └── processed/
│       ├── places_cleaned.csv            # Cleaned, geocoded Indian destinations (323 rows)
│       ├── train.parquet                 # Train split
│       ├── val.parquet                   # Validation split
│       ├── test.parquet                  # Test split
│       ├── train_features.parquet        # 31,008 interaction samples (96 personas)
│       ├── val_features.parquet          # 3,876 interaction samples (12 personas)
│       ├── test_features.parquet         # 3,876 interaction samples (12 personas)
│       └── feature_schema.json           # 17-feature schema definition
├── models/
│   ├── baseline_ridge.joblib             # Baseline Ridge model artifact
│   ├── champion_model.joblib             # Production Champion Model (Ridge alpha=0.01)
│   └── model_comparison_summary.csv     # Benchmark summary table
├── notebooks/
│   ├── 01_data_inspection.ipynb         # Raw data inspection & geocoding
│   ├── 02_preprocessing.ipynb           # Cleaning, transformations, and splits
│   ├── 03_eda_visualizations.ipynb      # Publication-grade EDA figures
│   ├── 04_baseline_models.ipynb          # Baseline models & scratch NumPy solver
│   └── 05_model_evaluation.ipynb        # Candidate architectures & Pareto frontier
├── reports/
│   ├── figures/                          # 7 high-res 300 DPI analytical charts
│   ├── BASELINE_REPORT.md                # Baseline evaluation report
│   ├── EDA_REPORT.md                     # Exploratory Data Analysis findings
│   └── MODEL_BENCHMARK_REPORT.md         # Final model comparison & selection report
├── src/
│   ├── data_loader.py                    # Dataset acquisition & geocoding registry
│   ├── inspect_data.py                   # Data inspection & profiling
│   ├── preprocessing.py                  # Cleaning, encoding, and Parquet splits
│   ├── eda_analysis.py                   # Statistical EDA generation
│   ├── feature_engineering.py            # Pairwise interaction matrices generator
│   ├── math_engine.py                    # Pure NumPy closed-form Ridge & NDCG@K
│   ├── baseline_model.py                 # Baseline heuristic evaluator
│   ├── model_evaluation.py               # Candidate model evaluation & hyperparameter tuning
│   └── inference.py                      # Production Inference Engine & Group Aggregator
└── tests/
    └── test_inference.py                 # Comprehensive unit test suite (9 test cases)
```

---

## 3. Champion Model & Performance

After benchmarking 5 candidate architectures across 3,876 test interactions, **Ridge Regression ($\alpha = 0.01$)** was selected as the **Production Champion Model**:

| Metric | Champion Model Performance |
| :--- | :--- |
| **Test RMSE** | **0.0001** |
| **Test MAE** | **0.00004** |
| **Test R²** | **1.0000** |
| **NDCG@5 / NDCG@10** | **1.0000 / 1.0000** |
| **Precision@5** | **1.0000** |
| **5-Member Group Latency** | **2.91 ms (Median), 5.33 ms (p95)** |
| **Serialized Model Size** | **0.67 KB** (Negligible memory footprint) |
| **Infrastructure Compatibility** | 100% compliant with Render Free Web Service (512 MB RAM limit) |

---

## 4. Quickstart & Usage

### 4.1 Running Inference in Python
```python
from ml_pipeline.src.inference import (
    RecommendationEngine,
    UserPreference,
    TravelConstraints,
    AggregationStrategy,
)

# 1. Initialize engine (loads model and catalog into memory)
engine = RecommendationEngine.get_instance()

# 2. Define group members
user_1 = UserPreference(user_id="u1", name="Aarav", pref_culture=0.8, pref_nature=0.2, budget_tier=0)
user_2 = UserPreference(user_id="u2", name="Priya", pref_nature=0.9, pref_adventure=0.6, budget_tier=1)

# 3. Define constraints (optional)
constraints = TravelConstraints(
    target_states=["Rajasthan"],
    max_budget_tier=1,
    exclude_weekly_off="Monday",
)

# 4. Generate recommendations
recommendations = engine.recommend_for_group(
    users=[user_1, user_2],
    strategy=AggregationStrategy.CONSENSUS,
    top_k=5,
    constraints=constraints,
)

for rec in recommendations:
    print(f"#{rec.rank} {rec.name} ({rec.city}, {rec.state}) - Score: {rec.score:.2f}")
    print(f"   Explanation: {rec.explanation}\n")
```

### 4.2 Running System Health Probe
```python
health = engine.health_check()
print(health)
# Output: {'status': 'healthy', 'model_name': 'Ridge Regression', 'catalog_destinations': 323, ...}
```

### 4.3 Running Unit Tests
```bash
.venv\Scripts\python -m unittest ml_pipeline.tests.test_inference
```
All 9 unit tests validate health check probes, single-user rankings, social choice aggregation rules, constraint filters, explainability schemas, and sub-10ms performance latencies.
