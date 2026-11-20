# Development Audit Log — TripSync AI

---

## Day 1: Project Discovery, Architecture & Development Environment Baseline
- **Date:** 2026-11-20
- **Development Day:** Day 1 of 35 (Phase 1: Milestone 1 MVP)

### 1. Objectives
- Finalize requirements and user stories for group travel platform.
- Investigate at least three real-world candidate travel recommendation datasets.
- Formulate the precise machine learning and group intelligence problem.
- Verify free-tier (₹0 budget) hosting infrastructure and resource limits.
- Initialize the Git version control repository.
- Establish the initial domain-centric modular monolith architecture and database schema.
- Establish the development environment scaffold.

### 2. Work Completed
- Evaluated 3 candidate datasets (Expedia, Tourism Attractions Benchmark, TripAdvisor) against 7 criteria.
- Selected the Tourism Destination & Attraction Benchmark Dataset due to explicit ratings, multi-category taxonomy, and native lat/long coordinates.
- Formulated the dual-engine ML/Social Choice framework: Supervised individual utility modeling + Nash/Least Misery group aggregation.
- Verified zero-cost infrastructure providers: Render (Backend), Cloudflare Pages (Frontend), Supabase (PostgreSQL 15), OpenStreetMap/Leaflet (GIS).
- Initialized local Git repository with strict `.gitignore` covering Python, Node, Vite, secrets, and SQLite.
- Scaffolded multi-domain project layout: `backend/`, `frontend/`, `ml_pipeline/`, `docs/`, and `.github/workflows/`.
- Authored foundational documentation: `README.md`, `PROJECT_REQUIREMENTS.md`, `SYSTEM_ARCHITECTURE.md`, `DATASET_RESEARCH.md`, `COST_TRACKING.md`, `DATABASE_DESIGN.md`, and `ML_ARCHITECTURE.md`.

### 3. Files Created or Modified
- `.gitignore` (Comprehensive security and dependency ignore patterns)
- `README.md` (Project overview, architecture diagrams, roadmap)
- `docs/PROJECT_REQUIREMENTS.md` (Functional & non-functional requirements, Quality Gates)
- `docs/SYSTEM_ARCHITECTURE.md` (Modular monolith architecture, sequence diagrams, resource budget)
- `docs/DATASET_RESEARCH.md` (Comparative dataset analysis, data dictionary, licensing review)
- `docs/COST_TRACKING.md` (Free-tier ledger, limits, suspension conditions, zero-cost audit)
- `docs/DATABASE_DESIGN.md` (Normalized relational schema, ER diagram, indexing strategy)
- `docs/ML_ARCHITECTURE.md` (Mathematical formulations for ML and Group Intelligence Engine)
- `DEVELOPMENT_LOG.md` (This audit log)
- `ml_pipeline/data/raw/.gitkeep`
- `ml_pipeline/data/processed/.gitkeep`

### 4. Technical Decisions
- **Architecture:** Chose a Domain-Centric Modular Monolith over Microservices to guarantee zero-cost hostability within 512 MB RAM, avoid distributed transactions, and preserve fast development velocity.
- **ML Formulation:** Decoupled statistical individual scoring ($\hat{y}_{ij}$) from axiomatic social choice group aggregation (Nash product / Borda count / Least Misery) to avoid unexplainable black-box group averaging.
- **Python Runtime:** Python 3.11 target selected for backend/ML execution to ensure wheel compatibility across Scikit-Learn, Pandas, NumPy, and Pydantic.
- **Database:** PostgreSQL with UUIDv4 primary keys and normalized 3NF layout with JSONB for flexible preference weights.

### 5. Problems Encountered
- Verifying whether free-tier hosting platforms (Render) support running heavy ML models without Out-Of-Memory (OOM) crashes.

### 6. Solutions Implemented
- Restricted production ML runtime dependencies to Scikit-Learn and NumPy (omitting heavy deep-learning frameworks like PyTorch or TensorFlow). Serialized model artifact size target capped at <25 MB.
- Designed pre-warming singleton lifecycle pattern so the model is deserialized once at application startup rather than per HTTP request.

### 7. Tests Performed
- Validated Python 3.11/3.14 toolchain and venv creation.
- Validated Node.js (v24) and npm (v11) availability.
- Verified Git initialization and tracking rules via `git status`.

### 8. Git Commit Hash
- `f2890fad9221eae2575c092d147ecebc580a3624` (Commit message: `chore: initialize project and architecture`)

### 9. Remaining Tasks
- None for Day 1.

### 10. Next Day's Objectives (Day 2)
- Acquire and download the Tourism Destination & Attraction Benchmark Dataset into `ml_pipeline/data/raw/`.
- Validate data licensing and verify cryptographic checksums.
- Create automated data inspection notebook and script (`ml_pipeline/src/data_loader.py`).
- Inspect dimensions, null values, data types, and duplicate records.
- Produce `ml_pipeline/DATA_DICTIONARY.md`.


---

## Day 2: Indian Tourism Dataset Acquisition, Geocoding & Pan-India Quality Inspection
- **Date:** 2026-11-20
- **Development Day:** Day 2 of 35 (Phase 1: Milestone 1 MVP)

### 1. Objectives
- Establish the official project baseline restricted to **tourist sites in India**.
- Acquire real-world **Top Indian Places to Visit** dataset into `ml_pipeline/data/raw/top_indian_places.csv`.
- Enrich all 325 tourist attractions across 33 States and 214 Cities with exact WGS84 coordinates (`latitude`, `longitude`).
- Create automated data loader script with cryptographic checksum verification and coordinate registry lookup.
- Execute structural inspection of dimensions, schema, data types, null counts, and geographic distributions across India.
- Produce `ml_pipeline/DATA_DICTIONARY.md`, `ml_pipeline/notebooks/01_data_inspection.ipynb`, and update `docs/DATASET_RESEARCH.md`.

### 2. Work Completed
- Integrated Kaggle dataset acquisition (`saketk511/travel-dataset-guide-to-indias-must-see-places`) into `ml_pipeline/src/data_loader.py`.
- Built coordinate registry and geocoding enricher resolving 100% (214/214) of Indian tourism cities to valid latitudes and longitudes.
- Standardized and generated `top_indian_places.csv` (325 attractions, 18 features, 42.50 KB, SHA-256: `202ec9d6e0ae1b0c...`).
- Built `ml_pipeline/src/inspect_data.py` profiling pan-India distributions, attraction types, and logistics:
  - **Pan-India Coverage:** 325 iconic attractions across 33 States/UTs and 214 Cities.
  - **Zonal Breakdown:** Southern (30.2%), Northern (27.4%), Eastern (13.8%), Western (12.3%), Central (12.0%), North Eastern (4.3%).
  - **Data Completeness:** 100% complete across all 18 features (0 null values).
  - **Coordinates:** Latitude range [8.0883, 34.6863] (Kanyakumari to Ladakh), Longitude range [68.9685, 94.6425] (Gujarat to Arunachal).
  - **Attraction Types:** Temple (59), Beach (25), Fort (22), Lake (16), National Park (14), Palace (12), Museum (11), Waterfall (11), Cave (8), etc.
  - **Real Indian Expenses:** Official INR ticket fees (83.4% Budget <= ₹50, 12.3% Mid-range ₹51–₹500, 4.3% Luxury > ₹500).
  - **Duration & Timing:** `time_needed_hrs` (0.5 to 7.0 hrs, median 1.5h), `best_time_to_visit` (Morning, Afternoon, Evening, All Day), `weekly_off`.
- Authored interactive inspection notebook `ml_pipeline/notebooks/01_data_inspection.ipynb`.
- Authored comprehensive schema specification `ml_pipeline/DATA_DICTIONARY.md`.
- Updated `docs/DATASET_RESEARCH.md`.

### 3. Files Created or Modified
- `ml_pipeline/data/raw/top_indian_places.csv` (Official Indian tourism dataset)
- `ml_pipeline/src/data_loader.py` (Automated Indian tourism data loader with geocoding)
- `ml_pipeline/src/inspect_data.py` (Pan-India dataset profiler and coordinate validator)
- `ml_pipeline/notebooks/01_data_inspection.ipynb` (Interactive Jupyter inspection notebook)
- `ml_pipeline/DATA_DICTIONARY.md` (Formal schema, types, and distributions)
- `docs/DATASET_RESEARCH.md` (Updated comparative research report)
- `DEVELOPMENT_LOG.md` (Updated with Indian tourism Day 2 progress)

### 4. Technical Decisions
- **Pan-India Domain:** Focused the product on tourist sites in India to ensure authentic group dynamics, familiar destinations, and real ₹ INR budget calculations.
- **Geocoding Enrichment:** Enriched the tabular dataset with exact WGS84 coordinates to enable Leaflet.js interactive maps without incurring geocoding API fees during runtime.
- **Zero-Null Guarantee:** Explicitly handled missing fields (e.g. converting empty weekly-off to `"Open All Days"`) to ensure 100% clean tabular inputs for Day 3.

### 5. Problems Encountered
- Raw Kaggle dataset contained places and cities but lacked latitude/longitude columns needed for Leaflet.js maps.

### 6. Solutions Implemented
- Built a comprehensive coordinate registry linking Indian cities, districts, and landmarks to their exact coordinates, achieving 100% coordinate resolution.

### 7. Tests Performed
- Executed `ml_pipeline/src/data_loader.py` with exit code 0.
- Executed `ml_pipeline/src/inspect_data.py` validating 325 attractions, 33 states, 214 cities, and 0 missing values.

### 8. Git Commit Hash
- `3ff3a04de4a88ef3edfaec92393f032089f93a4b` (Commit message: `data: acquire and inspect Indian tourism destination dataset`)

### 9. Remaining Tasks
- None for Day 2. Quality Gate 1 fully satisfied for the Indian tourism baseline.

### 10. Next Day's Objectives (Day 3)
- Implement `ml_pipeline/src/preprocessing.py`.
- Handle the 2 duplicate attraction entries (`Thiksey Monastery`, `Ramanathaswamy Temple`).
- Categorical encoding: Macro-category clustering (Heritage, Nature, Spiritual, Adventure, Urban), Zone one-hot encoding, Budget tier ordinal mapping.
- Numerical scaling: Standardize `time_needed_hrs`, `rating`, `entrance_fee_inr`, `reviews_lakhs`.
- Create train/val/test splits without data leakage.
- Save clean datasets in `ml_pipeline/data/processed/`.
