# Exploratory Data Analysis (EDA) Report — TripSync AI

**Document Version:** 1.0.0  
**Phase:** Gate 1 to Gate 2 Transition (Day 4)  
**Dataset Analyzed:** `ml_pipeline/data/processed/places_cleaned.csv` (323 Clean Destinations)  

---

## 1. Executive Summary
This Exploratory Data Analysis (EDA) investigates the statistical properties, spatial clustering, fee dynamics, and feature inter-relationships of the 323 premier Indian tourism destinations. The findings establish the mathematical foundations for Day 5 feature engineering and Day 6 recommendation algorithms.

---

## 2. Statistical Profiles & Key Metrics

| Dimension / Metric | Sample Mean | Median | Min | Max | Standard Deviation | Key Takeaway |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`rating` (Target)** | **4.49** | **4.50** | 1.40 | 4.90 | 0.28 | Left-skewed; 85% of attractions fall between 4.2 and 4.8. |
| **`time_needed_hrs`** | **1.81 hrs** | **1.50 hrs** | 0.50 hrs | 7.00 hrs | 0.97 hrs | Ideal for grouping into 2–3 POIs per day for itineraries. |
| **`entrance_fee_inr`** | **₹116.43** | **₹0.00** | ₹0 | ₹7,500 | ₹532.18 | **56.3% of attractions are free** (temples, beaches, public ghats). |
| **`reviews_lakhs`** | **0.41** (41k) | **0.17** (17k) | 0.01 | 7.40 (740k) | 0.65 | Long-tailed; Taj Mahal & India Gate dominate review volume. |

---

## 3. Visual Analysis & Empirical Distributions

All figures are generated at 300 DPI and stored in [`ml_pipeline/reports/figures/`](file:///c:/Projects/TripSync-AI/ml_pipeline/reports/figures).

### Figure 1: Target Variable (Rating) Distribution
- **Artifact:** [`01_target_rating_distribution.png`](file:///c:/Projects/TripSync-AI/ml_pipeline/reports/figures/01_target_rating_distribution.png)
- **Observations:** Continuous distribution clustered tightly between 4.3 and 4.7. Standard regression models targeting raw rating may suffer from compressed variance; we will utilize pairwise ranking / relative utility affinity modeling in Phase 1 ML.

### Figure 2: Thematic Category Distribution
- **Artifact:** [`02_macro_thematic_distribution.png`](file:///c:/Projects/TripSync-AI/ml_pipeline/reports/figures/02_macro_thematic_distribution.png)
- **Breakdown:**
  - `culture_heritage`: 135 destinations (41.8%)
  - `spiritual_religious`: 71 destinations (22.0%)
  - `nature_wildlife`: 64 destinations (19.8%)
  - `adventure_outdoor`: 34 destinations (10.5%)
  - `urban_entertainment`: 19 destinations (5.9%)
- **Takeaway:** Heritage, spiritual, and nature destinations constitute over 83% of India's premier tourist attractions.

### Figure 3: Pan-India Zonal & State Coverage
- **Artifact:** [`03_zonal_and_state_coverage.png`](file:///c:/Projects/TripSync-AI/ml_pipeline/reports/figures/03_zonal_and_state_coverage.png)
- **Breakdown:** Southern Zone (30.0%) and Northern Zone (27.2%) represent the two largest tourist clusters, followed by Eastern (13.9%), Western (12.4%), Central (12.1%), and North Eastern (4.3%).
- **Top States:** Uttar Pradesh (23), Maharashtra (20), West Bengal (20), Delhi (19), Karnataka (19), Himachal Pradesh (18), Andhra Pradesh (18), Kerala (16), Rajasthan (15).

### Figure 4: Financial & Budget Analysis
- **Artifact:** [`04_budget_tier_and_fees.png`](file:///c:/Projects/TripSync-AI/ml_pipeline/reports/figures/04_budget_tier_and_fees.png)
- **Breakdown:** 
  - `Budget` ($\le ₹50$): 269 attractions (83.3%)
  - `Mid-range` ($₹51 - ₹500$): 40 attractions (12.4%)
  - `Luxury` ($> ₹500$): 14 attractions (4.3%)
- **Takeaway:** Logarithmic transformation $\log(1 + \text{fee})$ successfully compressed outlier variance, allowing linear and tree-based models to treat financial tiers smoothly.

### Figure 5: Pacing & Visit Duration by Category
- **Artifact:** [`05_visit_duration_by_category.png`](file:///c:/Projects/TripSync-AI/ml_pipeline/reports/figures/05_visit_duration_by_category.png)
- **Observations:**
  - `adventure_outdoor` and `nature_wildlife` require significantly longer durations (median 2.5–4.0 hours) due to treks and safari routes.
  - `spiritual_religious` and `urban_entertainment` require shorter durations (median 1.0–1.5 hours).
  - This empirical difference directly informs the day-wise itinerary builder.

### Figure 6: Feature Correlation Heatmap
- **Artifact:** [`06_feature_correlation_heatmap.png`](file:///c:/Projects/TripSync-AI/ml_pipeline/reports/figures/06_feature_correlation_heatmap.png)
- **Key Correlations:**
  - `log_entrance_fee` and `budget_tier_code` exhibit expected high positive correlation ($r = 0.81$).
  - `time_needed_hrs` correlates positively with `adventure_outdoor` ($r = 0.38$) and negatively with `spiritual_religious` ($r = -0.24$).
  - `rating` shows modest positive correlation with `log_reviews` ($r = 0.22$), validating the popularity prior.
  - Zero multi-collinearity issues between spatial coordinates and thematic flags ($|r| < 0.15$).

### Figure 7: Geospatial Scatter Map of India
- **Artifact:** [`07_geospatial_attraction_scatter.png`](file:///c:/Projects/TripSync-AI/ml_pipeline/reports/figures/07_geospatial_attraction_scatter.png)
- **Observations:** Plotting Latitude vs. Longitude clearly sketches the geographical boundary of India, spanning from Ladakh ($34.68^\circ\text{N}$) to Kanyakumari ($8.08^\circ\text{N}$), and Gujarat ($68.96^\circ\text{E}$) to Assam/Arunachal ($94.64^\circ\text{E}$). The markers confirm spatial density in the Golden Triangle (Delhi-Agra-Jaipur) and the Western Ghats / Kerala corridor.

---

## 4. Architectural Implications for Day 5 & Day 6

1. **Preference Survey Design:** User preference surveys should collect weights across the 5 macro-dimensions: Culture, Nature, Spiritual, Adventure, and Urban.
2. **Budget Decay Function:** Because 83.3% of attractions are $\le ₹50$, budget filtering must act on daily trip budget allocations rather than individual ticket barriers.
3. **Spatial Route Optimization:** Attractions clustered within the same state/city should be grouped together into daily time slots using Haversine distance.
