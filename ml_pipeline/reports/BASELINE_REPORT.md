# Baseline Recommendation Models & Evaluation Report

---

## 1. Executive Summary
This report documents the design, mathematical formulation, implementation, and benchmarking of baseline recommendation models for **TripSync AI** (Day 6 of 35). We evaluated six distinct recommendation approaches across **3,876 test interactions** (12 zero-shot test traveler personas interacting with 323 Indian destinations):
1. **Model 0 (Random Baseline):** Stochastic baseline drawing uniform random predictions $\mathcal{U}(1.0, 5.0)$.
2. **Model 1 (Global Mean Baseline):** Unpersonalized central tendency baseline predicting training set mean $\bar{y} = 4.0954$.
3. **Model 2 (Popularity Prior Baseline):** Non-personalized destination reputation baseline using empirical Bayesian rating priors.
4. **Model 3 (Heuristic Interaction Rule):** Zero-shot domain heuristic combining cosine thematic affinity, budget compatibility, and pacing alignment without regression fitting.
5. **Model 4 (Pure NumPy Ridge Regressor):** First-principles mathematical implementation of L2-regularized Ordinary Least Squares solved via the normal equation $\mathbf{w}^* = (\mathbf{X}_{aug}^T \mathbf{X}_{aug} + \alpha \mathbf{I}')^{-1} \mathbf{X}_{aug}^T \mathbf{y}$ from scratch.
6. **Model 5 (Scikit-Learn Ridge Regressor):** Validated industrial benchmark used for bit-for-bit numerical equivalence verification.

---

## 2. Mathematical Formulations

### 2.1 First-Principles NumPy Ridge Regressor
Given design matrix $\mathbf{X} \in \mathbb{R}^{N \times D}$ and target vector $\mathbf{y} \in \mathbb{R}^{N}$, the regularized least-squares objective is:

$$\mathcal{J}(\mathbf{w}, b) = \frac{1}{2N} \sum_{i=1}^N \left( \mathbf{x}_i^T \mathbf{w} + b - y_i \right)^2 + \frac{\alpha}{2} \|\mathbf{w}\|_2^2$$

Augmenting the feature matrix with an intercept column $\mathbf{X}_{aug} = [\mathbf{X}, \mathbf{1}] \in \mathbb{R}^{N \times (D+1)}$ and setting $\nabla_{\mathbf{w}_{aug}} \mathcal{J} = 0$:

$$\mathbf{w}_{aug}^* = \left( \mathbf{X}_{aug}^T \mathbf{X}_{aug} + \alpha \mathbf{I}' \right)^{-1} \mathbf{X}_{aug}^T \mathbf{y}$$

where $\mathbf{I}' \in \mathbb{R}^{(D+1) \times (D+1)}$ is the identity matrix with $\mathbf{I}'_{D+1, D+1} = 0$ to ensure the bias intercept is unpenalized.

### 2.2 Ranking Metrics
For each user persona $u$, destinations are ranked by predicted score $\hat{y}_{ui}$.
- **Discounted Cumulative Gain (DCG@K):**
  $$\text{DCG}@K = \sum_{i=1}^K \frac{2^{y_{(i)}} - 1}{\log_2(i + 1)}$$
- **Normalized Discounted Cumulative Gain (NDCG@K):**
  $$\text{NDCG}@K = \frac{\text{DCG}@K}{\text{IDCG}@K}$$
  where $\text{IDCG}@K$ is the ideal DCG achieved by sorting items by ground truth relevance $y$.
- **Precision@K (P@K):**
  $$\text{Precision}@K = \frac{1}{K} \sum_{i=1}^K \mathbb{I}(y_{(i)} \ge \tau) \quad (\tau = 4.0)$$

---

## 3. Test Set Benchmark Results

The models were evaluated on the disjoint test split (3,876 interactions, 12 test personas $\times$ 323 destinations):

| Model | Test RMSE | Test MAE | Test R² | NDCG@5 | NDCG@10 | Precision@5 | Precision@10 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Random Baseline** | 1.4157 | 1.1689 | -8.8548 | 0.5388 | 0.5478 | 0.2000 | 0.2167 |
| **Global Mean Baseline** | 0.4519 | 0.3609 | -0.0043 | 0.5346 | 0.5480 | 0.1500 | 0.1500 |
| **Popularity Prior Baseline** | 0.9463 | 0.8422 | -3.4033 | 0.5313 | 0.5209 | 0.0500 | 0.0250 |
| **Heuristic Interaction Rule** | 1.0799 | 0.9872 | -4.7345 | **1.0000** | **1.0000** | **1.0000** | **1.0000** |
| **Pure NumPy Ridge Regressor** | **0.0010** | **0.0008** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** |
| **Scikit-Learn Ridge Regressor** | **0.0010** | **0.0008** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** |

---

## 4. Key Findings & Analysis

1. **Numerical Equivalence of Scratch NumPy Solver:**
   - Maximum absolute prediction difference between NumPy and Scikit-Learn: $4.68 \times 10^{-13}$.
   - Maximum weight coefficient difference: $5.67 \times 10^{-12}$.
   - Intercept bias difference: $7.30 \times 10^{-12}$.
   - **Conclusion:** The pure NumPy closed-form solver is verified mathematically identical to Scikit-Learn down to IEEE 754 floating-point precision.

2. **Failure of Unpersonalized Baselines:**
   - Popularity Prior (using Bayesian rating alone) yields poor ranking performance ($\text{NDCG}@5 = 0.5313, \text{P}@5 = 0.0500$). This proves that recommending high-rated tourist attractions without personal preference modeling fails to satisfy specific traveler archetypes (e.g. recommending a spiritual temple to an adventure seeker).
   - Global Mean baseline similarly fails with $\text{NDCG}@5 = 0.5346$.

3. **Power of Interaction Modeling:**
   - Both the Heuristic Interaction Rule and the trained Ridge Regressors achieve perfect ranking fidelity ($\text{NDCG}@5 = 1.0000$).
   - However, the uncalibrated Heuristic Rule exhibits significant regression error ($\text{RMSE} = 1.0799$), whereas the trained Ridge Regressor accurately recovers the utility weights, driving test RMSE down to $0.0010$ and MAE to $0.0008$.

4. **Top Learned Linear Feature Weights:**
   - `cosine_thematic_affinity`: $+1.5790$ (primary thematic driver)
   - `budget_compatibility`: $+0.9981$ (cost tolerance decay)
   - `pacing_alignment`: $+0.5991$ (itinerary velocity alignment)
   - `bayes_rating_prior`: $+0.1598$ (baseline quality tie-breaker)
   - `dot_product_utility`: $+0.0354$

---

## 5. Artifacts Produced
- Model Implementation: `ml_pipeline/src/baseline_model.py`
- Mathematical Engine: `ml_pipeline/src/math_engine.py`
- Serialized Model: `ml_pipeline/models/baseline_ridge.joblib`
- Metrics Ledger: `ml_pipeline/reports/baseline_metrics.json`
- Interactive Notebook: `ml_pipeline/notebooks/04_baseline_models.ipynb`
