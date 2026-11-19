# Machine Learning & Group Intelligence Architecture — TripSync AI

**Document Version:** 1.0.0  
**Phase:** Gate 1 & Gate 2 Baseline  
**Key Paradigms:** Dual-Engine Architecture (Empirical ML Inference + Social Choice Group Engine)  

---

## 1. System Mathematical Foundations

Group recommendation fundamentally differs from individual recommendation because there is no single loss function that monotonically represents group utility. TripSync AI divides the problem into two decoupled computational phases:

```
Step 1: Individual Affinity Estimation (Supervised / Content-Collaborative ML)
          Inputs: Individual User Vectors u_i + Item Vectors d_j
          Output: Predicted Individual Utility Matrix M where M[i, j] = y_hat(i, j)

Step 2: Social Choice Group Aggregation (Game Theory & Multi-Criteria Optimization)
          Inputs: Matrix M for all members i in Group G + Trip Constraints C
          Output: Pareto-Optimal Group Ranking + Conflict Annotations
```

---

## 2. Phase 1: Individual Affinity Prediction

### Mathematical Formulation
Let $\mathbf{u}_i \in \mathbb{R}^d$ be the preference vector of user $i$, and $\mathbf{d}_j \in \mathbb{R}^d$ be the attribute vector of candidate attraction/destination $j$.

1. **Category Match Formulation (Cosine Similarity):**
   $$\text{Sim}_{\text{cat}}(\mathbf{u}_i, \mathbf{d}_j) = \frac{\mathbf{u}_i^{\text{cat}} \cdot \mathbf{d}_j^{\text{cat}}}{\|\mathbf{u}_i^{\text{cat}}\|_2 \|\mathbf{d}_j^{\text{cat}}\|_2}$$

2. **Budget Compatibility Function:**
   Let $b_i^{\text{max}}$ be user $i$'s maximum budget per day, and $c_j$ be the cost per day of destination $j$:
   $$\phi_{\text{budget}}(b_i^{\text{max}}, c_j) = \begin{cases} 
   1.0 & \text{if } c_j \le b_i^{\text{max}} \\ 
   \exp\left(-\lambda \frac{c_j - b_i^{\text{max}}}{b_i^{\text{max}}}\right) & \text{if } c_j > b_i^{\text{max}} 
   \end{cases}$$
   where $\lambda > 0$ controls the penalty decay for exceeding budget.

3. **Composite Affinity Prediction ($\hat{y}_{ij}$):**
   In the library-based implementation, we train a regularized regressor / gradient-boosted tree:
   $$\hat{y}_{ij} = f_{\boldsymbol{\theta}}(\mathbf{x}_{ij})$$
   where $\mathbf{x}_{ij} = \left[ \text{Sim}_{\text{cat}}(\mathbf{u}_i, \mathbf{d}_j), \phi_{\text{budget}}(b_i^{\text{max}}, c_j), \bar{r}_j, \text{PaceMatch}(u_i^{\text{pace}}, d_j^{\text{duration}}) \right]$.

---

## 3. Phase 2: Group Intelligence Engine (Social Choice Aggregation)

Once individual utility predictions $\hat{y}_{ij}$ are computed for all members $i \in G = \{1, \dots, N\}$ and candidates $j \in \{1, \dots, M\}$:

### Strategy A: Additive Utilitarianism (Average Satisfaction)
Maximizes total group utility, assuming equal voting weight:
$$\text{Score}_{\text{util}}(j) = \frac{1}{|G|} \sum_{i \in G} \hat{y}_{ij}$$

### Strategy B: Egalitarianism (Least Misery Strategy)
Guarantees that the least satisfied member is as happy as possible (avoids personal vetoes):
$$\text{Score}_{\text{egal}}(j) = \min_{i \in G} \hat{y}_{ij}$$

### Strategy C: Hybrid Nash Bargaining Optimization (TripSync Default)
Balancing collective happiness while heavily penalizing options that alienate any member:
$$\text{Score}_{\text{Nash}}(j) = \prod_{i \in G} \left( \hat{y}_{ij} - \tau_i \right)^{w_i}$$
where $\tau_i$ is member $i$'s disagreement reservation threshold (e.g., minimum acceptable rating of 2.5), and $w_i$ represents optional member weight.

### Strategy D: Polarization & Conflict Detection Metric
To alert groups when an option is highly polarizing (e.g. loved by 2, hated by 2):
$$\sigma^2(j) = \frac{1}{|G| - 1} \sum_{i \in G} \left( \hat{y}_{ij} - \text{Score}_{\text{util}}(j) \right)^2$$
If $\sigma^2(j) > \theta_{\text{conflict}}$, the platform marks the recommendation with a `[POLARIZING]` tag and renders an explanation to facilitate group discussion.

---

## 4. Dual Implementation Contract

To satisfy academic rigor and production resilience:
1. **`ml_pipeline/src/math_engine.py`:** Pure NumPy matrix implementation of Cosine Similarity, Borda Rank aggregation, and Nash Bargaining product without external ML libraries.
2. **`ml_pipeline/src/train.py`:** Scikit-Learn / LightGBM pipeline with preprocessing transformer, cross-validation, and `.joblib` serialization for production deployment.
