# Data Dictionary & Schema Specification — TripSync AI

**Document Version:** 2.0.0 (Global Baseline)  
**Status:** Validated Raw Data Baseline (Gate 1 Passed)  
**Dataset Name:** Worldwide Travel Cities (Ratings and Climate)  
**Source:** Open Data / Kaggle (`furkanima/worldwide-travel-cities-ratings-and-climate`)  
**Scope:** 560 Global Destinations across 167 Countries  

---

## 1. File Catalog & Physical Attributes

| File Name | Physical Size | Dimensions | Record Granularity | Natural Key | Missing Values |
| :--- | :---: | :---: | :--- | :--- | :---: |
| **`worldwide_travel_cities.csv`** | 478.87 KB | 560 rows × 19 cols | Distinct Global Tourist City / Destination | `id` (UUID) | **0 (0.0%)** |

---

## 2. Comprehensive Column Definitions

| Column Name | Inferred Type | Target DB Type | Null Count (%) | Unique Values | Value Domain & Range | Semantic Description |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **`id`** | `string` / `uuid` | UUID | 0 (0.0%) | 560 | Standard UUIDv4 | Unique surrogate identifier for each destination. |
| **`city`** | `string` | VARCHAR(100) | 0 (0.0%) | 557 | Paris, Tokyo, Milan, Rome, etc. | Name of the tourist destination / urban hub. |
| **`country`** | `string` | VARCHAR(100) | 0 (0.0%) | 167 | USA, Italy, Japan, France, etc. | Sovereign country of destination. |
| **`region`** | `string` | VARCHAR(50) | 0 (0.0%) | 7 | `europe` (177), `north_america` (104), `asia` (99), `africa` (63), `south_america` (55), `oceania` (51), `middle_east` (11) | Continental macro-region. |
| **`short_description`** | `string` | TEXT | 0 (0.0%) | 560 | Narrative summaries | Editorial overview of the city's key atmosphere, attractions, and cultural vibe. |
| **`latitude`** | `float64` | NUMERIC(9,6) | 0 (0.0%) | 560 | [-54.8073, 78.7199] | Geographic Latitude (WGS84). Ready for Leaflet maps. |
| **`longitude`** | `float64` | NUMERIC(9,6) | 0 (0.0%) | 560 | [-175.2018, 179.3329] | Geographic Longitude (WGS84). Ready for Leaflet maps. |
| **`avg_temp_monthly`** | `string` (JSON) | JSONB | 0 (0.0%) | 560 | `{"1": {"avg": X, "max": Y, "min": Z}, ...}` | Monthly climatological temperature curves (months 1–12). |
| **`ideal_durations`** | `string` (JSON) | JSONB | 0 (0.0%) | 8 combinations | `["Weekend"]`, `["Short trip"]`, `["One week"]`, `["Long trip"]` | Optimal duration intervals for travel planning. |
| **`budget_level`** | `string` | VARCHAR(20) | 0 (0.0%) | 3 | `Mid-range` (339), `Budget` (145), `Luxury` (76) | Financial affordability tier. |
| **`culture`** | `int64` | SMALLINT | 0 (0.0%) | 4 | [2, 5], Mean = 3.85 | Thematic score for heritage, museums, and historical interest. |
| **`adventure`** | `int64` | SMALLINT | 0 (0.0%) | 4 | [2, 5], Mean = 3.18 | Thematic score for extreme sports, hiking, and active exploration. |
| **`nature`** | `int64` | SMALLINT | 0 (0.0%) | 4 | [2, 5], Mean = 3.73 | Thematic score for scenery, parks, wildlife, and natural landscapes. |
| **`beaches`** | `int64` | SMALLINT | 0 (0.0%) | 5 | [1, 5], Mean = 2.38 | Thematic score for coastline, swimming, and marine relaxation. |
| **`nightlife`** | `int64` | SMALLINT | 0 (0.0%) | 5 | [1, 5], Mean = 3.02 | Thematic score for bars, clubs, late-night dining, and evening energy. |
| **`cuisine`** | `int64` | SMALLINT | 0 (0.0%) | 4 | [2, 5], Mean = 3.79 | Thematic score for culinary richness, street food, and gastronomy. |
| **`wellness`** | `int64` | SMALLINT | 0 (0.0%) | 4 | [2, 5], Mean = 3.07 | Thematic score for spa, relaxation, retreat, and tranquility. |
| **`urban`** | `int64` | SMALLINT | 0 (0.0%) | 5 | [1, 5], Mean = 3.15 | Thematic score for metropolis vibes, shopping, and modern architecture. |
| **`seclusion`** | `int64` | SMALLINT | 0 (0.0%) | 5 | [1, 5], Mean = 3.03 | Thematic score for peaceful off-the-beaten-path intimacy. |

---

## 3. Machine Learning Preprocessing Roadmap (Day 3)

1. **Feature Parsing:**
   - Parse `ideal_durations` from JSON strings to multi-label binary indicators (`duration_weekend`, `duration_short`, `duration_week`, `duration_long`).
   - Extract mean seasonal temperatures from `avg_temp_monthly` to support seasonal group trip planning.
2. **Categorical Encoding:**
   - Ordinal mapping for `budget_level`: `{'Budget': 1, 'Mid-range': 2, 'Luxury': 3}`.
   - One-Hot encoding for `region`.
3. **Thematic Vector Normalization:**
   - Standardize the 9 thematic scores into a normalized destination feature vector $\mathbf{d}_j \in [0, 1]^9$.
4. **Group Matching Utility Formulation:**
   - Map user preference survey Likert ratings directly against the 9 normalized thematic dimensions to compute pairwise cosine affinity and budget compatibility decay functions.
