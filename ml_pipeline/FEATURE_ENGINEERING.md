# Feature Engineering Specification — TripSync AI

**Document Version:** 1.0.0  
**Phase:** Gate 1 to Gate 2 Transition (Day 5)  
**Artifacts Generated:** `train_features.parquet`, `val_features.parquet`, `test_features.parquet`, `feature_schema.json`  

---

## 1. Feature Engineering Problem Formulation

In a group recommendation system, recommending an attraction $j$ to a traveler $i$ requires transforming raw, static item features and dynamic user survey inputs into **pairwise interaction representations**:

$$\mathbf{x}_{ij} = \Psi(\mathbf{u}_i, \mathbf{d}_j)$$

where:
- $\mathbf{u}_i$ is user $i$'s preference survey response: category weights $\mathbf{u}_i^{\text{cat}} \in [0, 1]^5$, budget tier $b_i \in \{0, 1, 2\}$, and pacing preference $p_i \in \{0, 1, 2\}$.
- $\mathbf{d}_j$ is destination $j$'s attributes: category indicators $\mathbf{d}_j^{\text{cat}} \in \{0, 1\}^5$, budget tier $c_j \in \{0, 1, 2\}$, duration $t_j \in [0.5, 7.0]$, rating $\bar{r}_j$, and log review count.
- $\mathbf{x}_{ij} \in \mathbb{R}^{17}$ is the engineered feature vector fed into ML recommendation algorithms.

---

## 2. Interaction Feature Mathematical Formulations

### 2.1 Thematic Cosine Affinity
Measures the directional alignment between user preference distribution and destination category vector:
$$\text{Sim}_{\text{cosine}}(\mathbf{u}_i, \mathbf{d}_j) = \frac{\mathbf{u}_i^{\text{cat}} \cdot \mathbf{d}_j^{\text{cat}}}{\|\mathbf{u}_i^{\text{cat}}\|_2 \|\mathbf{d}_j^{\text{cat}}\|_2 + \epsilon}$$

### 2.2 Budget Compatibility Decay ($\phi_{\text{budget}}$)
Models non-linear financial tolerance. If a destination's cost tier exceeds a user's budget tier, a smooth exponential decay penalty is applied:
$$\phi_{\text{budget}}(b_i, c_j) = \exp\left(-\lambda \cdot \max(0, c_j - b_i)\right)$$
where $\lambda = 0.65$. Under this decay:
- Within budget ($c_j \le b_i$): Penalty $= 1.0$ (Zero friction).
- 1 tier above budget ($c_j - b_i = 1$): Penalty $= e^{-0.65} \approx 0.52$.
- 2 tiers above budget ($c_j - b_i = 2$): Penalty $= e^{-1.30} \approx 0.27$.

### 2.3 Pacing Alignment Score ($\psi_{\text{pace}}$)
Quantifies whether attraction duration matches user travel pacing:
$$\psi_{\text{pace}}(p_i, t_j) = \text{clip}\left(1.0 - \frac{|t_j - \tau(p_i)|}{6.0}, 0.0, 1.0\right)$$
where the target duration mapping is:
- Relaxed ($p_i = 0$): $\tau = 1.25\text{ hrs}$.
- Moderate ($p_i = 1$): $\tau = 2.25\text{ hrs}$.
- Active / Fast-paced ($p_i = 2$): $\tau = 4.50\text{ hrs}$.

### 2.4 Empirical Bayesian-Damped Rating Prior
Combines individual attraction rating $\bar{r}_j$ and popularity volume $v_j$ (reviews in lakhs) against global benchmark mean $C = 4.49$:
$$r_j^{\text{Bayes}} = \frac{v_j}{v_j + m} \bar{r}_j + \frac{m}{v_j + m} C$$
where $m = 0.20$ lakhs (20,000 reviews) acts as the shrinkage threshold, stabilizing ratings for lower-review attractions.

---

## 3. Comprehensive Feature Schema (`feature_schema.json`)

| Feature Column Name | Data Type | Value Range | Invariance & Domain |
| :--- | :---: | :---: | :--- |
| **`cosine_thematic_affinity`** | `float64` | $[0.0, 1.0]$ | Primary thematic affinity metric. |
| **`dot_product_utility`** | `float64` | $[0.0, 1.0]$ | Unnormalized category dot product. |
| **`budget_compatibility`** | `float64` | $[0.27, 1.0]$ | Exponential budget tolerance score. |
| **`pacing_alignment`** | `float64` | $[0.0, 1.0]$ | Travel pace alignment score. |
| **`bayes_rating_prior`** | `float64` | $[1.40, 4.88]$ | Bayesian-shrunk rating prior. |
| **`destination_duration_hrs`** | `float64` | $[0.50, 7.00]$ | Visiting duration in hours. |
| **`destination_log_reviews`** | `float64` | $[0.01, 2.13]$ | $\log_{10}(1 + \text{reviews\_lakhs})$. |
| **`destination_log_fees`** | `float64` | $[0.00, 8.92]$ | $\log(1 + \text{entrance\_fee\_inr})$. |
| **`destination_latitude`** | `float64` | $[8.0883, 34.6863]$ | Latitude coordinate in India. |
| **`destination_longitude`** | `float64` | $[68.9685, 94.6425]$ | Longitude coordinate in India. |
| **`user_pref_culture`** | `float64` | $[0.0, 1.0]$ | User survey culture importance weight. |
| **`user_pref_nature`** | `float64` | $[0.0, 1.0]$ | User survey nature importance weight. |
| **`user_pref_spiritual`** | `float64` | $[0.0, 1.0]$ | User survey spiritual importance weight. |
| **`user_pref_adventure`** | `float64` | $[0.0, 1.0]$ | User survey adventure importance weight. |
| **`user_pref_urban`** | `float64` | $[0.0, 1.0]$ | User survey urban importance weight. |
| **`user_budget_tier`** | `int64` | $\{0, 1, 2\}$ | User budget constraint tier. |
| **`user_pacing_pref`** | `int64` | $\{0, 1, 2\}$ | User travel pacing tier. |
| **`target_affinity_score`** | `float64` | $[1.00, 5.00]$ | **Ground Truth Target.** Empirical composite affinity. |

---

## 4. Feature Importance Profiling (Random Forest Analysis)

A 50-tree Random Forest Regressor evaluated feature attribution on the training split:

```
Ranked Feature Importance:
  1. cosine_thematic_affinity : 78.34%  ████████████████████████████████
  2. budget_compatibility     : 15.94%  ██████
  3. pacing_alignment         :  4.96%  ██
  4. dot_product_utility      :  0.47%  ▏
  5. bayes_rating_prior       :  0.22%  ▏
  6. destination_duration_hrs :  0.02%  
  7. user_pref_nature         :  0.02%  
  8. destination_log_reviews  :  0.01%  
  9. destination_log_fees     :  0.01%  
```

**Key Finding:** Over **94% of predictive signal** is captured by the interaction triplet: **Thematic Affinity + Budget Compatibility + Pacing Alignment**. Raw standalone user demographics and raw destination IDs have near-zero standalone predictive power without interaction modeling.

---

## 5. Strict User-Level Disjoint Splitting (Leakage Prevention)

To test true generalization for group planning platforms:
- Random row-wise shuffling causes data leakage because the same user's interactions appear in both training and test sets.
- We enforce a **Disjoint User-Level Split**:
  - **Train Split (80%):** 96 distinct user profiles ($31,008$ interaction pairs).
  - **Validation Split (10%):** 12 distinct user profiles ($3,876$ interaction pairs).
  - **Test Split (10%):** 12 distinct user profiles ($3,876$ interaction pairs).
- **Validation Guarantee:** Models on Day 6 & 7 will be evaluated exclusively on traveler profiles they have never seen during training.
