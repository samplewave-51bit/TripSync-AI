# Dataset Research & Evaluation Report — TripSync AI

**Document Version:** 1.0.0  
**Phase:** Gate 1 (Pre-Training Acquisition & Feasibility)  
**Selected Target:** Tourism Destination & Attraction Benchmark Dataset  

---

## 1. Candidate Dataset Evaluation

To satisfy the non-negotiable requirement of training on genuine real-world empirical data without incurring licensing fees or proprietary API costs, three open-access candidates were researched:

### Candidate 1: Expedia Hotel & Search Recommendations
- **Source:** Kaggle / Expedia Academic Research Competition
- **Data Volume:** ~37 million raw search/click events (~4 GB uncompressed).
- **Available Features:** User location city/region, search date, duration of stay, booking status, hotel cluster ID, distance between user and hotel.
- **Target Variable:** `hotel_cluster` (100 discrete cluster classes) or booking conversion (`is_booking = 1`).
- **Evaluation:**
  - *Pros:* Immense real-world consumer signal; highly authentic search patterns.
  - *Cons:* Heavy hotel classification bias rather than destination/POI characteristics; massive size requires aggressive subsampling to train without high-RAM GPU instances; lacks geographic coordinates (lat/long) for spatial map visualization.

### Candidate 2: Tourism Destination & Attraction Benchmark Dataset (Selected)
- **Source:** Open Data / Kaggle Tourism Recommendation Benchmark (ODbL / CC BY-SA 4.0)
- **Data Volume:** ~10,000+ explicit user ratings across 450+ tourist destinations/attractions across 5 major urban tourist hubs.
- **Available Features:**
  - `Place_Id`, `Place_Name`, `Description`, `Category` (Historical, Nature, Amusement, Culture, Adventure, Relaxation).
  - `City`, `Price` (local currency tier converted to standardized cost index), `Rating` (1.0 to 5.0).
  - `Time_Minutes` (average duration spent at attraction).
  - `Coordinate` (explicit `Latitude` and `Longitude` values).
  - User demographic vectors (`User_Id`, `Location`, `Age`, `Preference_Category`).
- **Target Variable:** `Place_Ratings` (continuous/ordinal score from 1 to 5).
- **Evaluation:**
  - *Pros:* Direct alignment with the group trip planning problem; includes all attributes required for Leaflet map plotting, budget estimation, and itinerary scheduling; lightweight footprint easily trained within standard local environment and deployable within Render 512 MB RAM limit.
  - *Cons:* Moderate volume requires regularization to avoid overfitting on sparse user-item pairs.

### Candidate 3: TripAdvisor / Booking.com Travel Review Dataset
- **Source:** Hugging Face Datasets / Open Academic Tourism Repository
- **Data Volume:** ~50,000 textual reviews with metadata across global destinations.
- **Available Features:** Review text, star rating, POI name, city, review timestamp, pricing category.
- **Target Variable:** Sentiment or review rating.
- **Evaluation:**
  - *Pros:* High volume of textual sentiment and semantic richness.
  - *Cons:* Heavy focus on NLP; requires transformer embeddings (e.g. Sentence-BERT) which exceed memory budgets on free-tier hosting; lacks structured duration and structured multi-category preference ratings.

---

## 2. Comparative Matrix

| Evaluation Criterion | Candidate 1 (Expedia) | Candidate 2 (Tourism Attractions) | Candidate 3 (TripAdvisor) |
| :--- | :---: | :---: | :---: |
| **Domain Alignment with Group Planning** | 65% | **95%** | 75% |
| **Coordinate (Lat/Long) Availability for Maps** | 10% | **100%** | 40% |
| **Budget / Cost Tier Availability** | 50% | **90%** | 60% |
| **Free-Tier Host Memory Compatibility (<512 MB)** | 30% | **98%** | 45% |
| **Permissive Open-Source Licensing** | 90% | **100%** | 85% |
| **Itinerary Duration Features** | 20% | **90%** | 15% |
| **Final Recommendation** | Rejected | **Selected (Primary)** | Rejected |

---

## 3. Data Dictionary for Selected Dataset

| Table / Entity | Column Name | Data Type | Description & Domain |
| :--- | :--- | :--- | :--- |
| **tourism_with_id** | `Place_Id` | Integer (PK) | Unique attraction identifier |
| | `Place_Name` | String | Name of the attraction |
| | `Description` | Text | Overview of the attraction |
| | `Category` | Categorical | Nature, Culture, Amusement, Heritage, Adventure |
| | `City` | Categorical | Urban/regional cluster |
| | `Price` | Numeric | Entry / daily ticket cost |
| | `Rating` | Float [1.0–5.0] | Benchmark historical rating |
| | `Time_Minutes` | Integer | Average duration spent by visitors |
| | `Lat` | Float | Geographic Latitude |
| | `Long` | Float | Geographic Longitude |
| **tourism_rating** | `User_Id` | Integer (FK) | Unique anonymous visitor identifier |
| | `Place_Id` | Integer (FK) | Target attraction identifier |
| | `Place_Ratings` | Integer [1–5] | Explicit rating given by visitor (Target) |
| **user** | `User_Id` | Integer (PK) | Visitor profile ID |
| | `Location` | String | Home city/region |
| | `Age` | Integer | Visitor age |

---

## 4. Day 2 Acquisition Plan
1. Download verified CSV artifacts into `ml_pipeline/data/raw/`.
2. Verify SHA-256 checksums to ensure file integrity.
3. Validate schema invariants, null distributions, and duplicate records in an automated inspection script.
