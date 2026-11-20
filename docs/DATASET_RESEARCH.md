# Dataset Research & Evaluation Report — TripSync AI

**Document Version:** 3.0.0 (India Tourism Baseline)  
**Phase:** Gate 1 (Pre-Training Acquisition & Feasibility)  
**Selected Target:** Top Indian Places to Visit (Indian Tourism Guide)  
**Source:** Open Data / Kaggle (`saketk511/travel-dataset-guide-to-indias-must-see-places`)  

---

## 1. Candidate Dataset Evaluation

To satisfy the explicit user requirement of **restricting TripSync AI to tourist sites in India** with authentic cultural context, empirical ratings, and verifiable coordinates, candidate datasets were researched and evaluated:

### Candidate 1: Regional Indonesian Dataset (Earlier Prototype)
- **Scope:** 437 tourist places in Java, Indonesia.
- **Evaluation:** Clean rating matrix, but limited to Indonesia. *Superseded by user request to focus on Indian tourism.*

### Candidate 2: Worldwide Travel Cities Dataset
- **Scope:** 560 cities worldwide.
- **Evaluation:** Broad global scope, but lacks granular attraction-level duration and domestic Indian travel expense context. *Superseded.*

### Candidate 3: Top Indian Places to Visit (Selected Baseline)
- **Scope:** **325 premier tourist attractions across 33 States and 214 Cities in India**.
- **Available Features:**
  - `name`, `zone`, `state`, `city`, `type`
  - Rating & Popularity: `Google review rating` [1.4 to 4.9], `Number of google review in lakhs` [0.01 to 7.4 lakhs]
  - Expense & Logistics: `Entrance Fee in INR` [₹0 to ₹7,500], `budget_tier` (Budget, Mid-range, Luxury)
  - Pacing: `time needed to visit in hrs` [0.5 to 7.0 hrs]
  - Scheduling: `best_time_to_visit` (Morning, Afternoon, Evening, All Day), `weekly_off`
  - Connectivity & Rules: `airport_within_50km`, `dslr_allowed`, `significance`
  - Geospatial: Enriched with WGS84 `latitude` and `longitude` across India.
- **Evaluation:** *Selected as our official project baseline.*

---

## 2. Comparative Matrix

| Evaluation Criterion | Candidate 1 (Indonesia) | Candidate 2 (Worldwide Cities) | Candidate 3 (Top Indian Places) |
| :--- | :---: | :---: | :---: |
| **Relevance to Indian Group Travel Context** | 10% | 40% | **100% (Pan-India focus)** |
| **Real INR Expense Compatibility** | 0% (IDR) | 10% (USD Tiers) | **100% (Official INR ticket fees)** |
| **Duration / Itinerary Features** | 47% (53% missing) | 50% (Categorical only) | **100% (Exact visit hours 0.5–7h)** |
| **Coordinate Availability for Leaflet Maps** | 100% | 100% | **100% (Enriched pan-India bounds)** |
| **Memory Footprint for Free Host** | 98% (<1 MB) | 98% (<1 MB) | **99% (42.5 KB raw size)** |
| **Zero-Missing Value Cleanliness** | 85% | 100% | **100% (0 nulls)** |
| **Final Recommendation** | Superseded | Superseded | **Selected Baseline** |

---

## 3. Data Integrity & Verification
- **Target File:** `ml_pipeline/data/raw/top_indian_places.csv`
- **Total Attractions:** 325
- **States & Union Territories:** 33
- **Cities Represented:** 214
- **Completeness:** 100% (0 null values across all 18 features)
- **Geographic Bounds:** Latitude $[8.0883, 34.6863]$, Longitude $[68.9685, 94.6425]$
- **SHA-256 Checksum:** `202ec9d6e0ae1b0c3c575d880dab54752249ad063666408f374c7ad407b64976`
