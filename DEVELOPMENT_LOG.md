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

## Day 2: Dataset Acquisition, Integrity Verification & Quality Inspection
- **Date:** 2026-11-20
- **Development Day:** Day 2 of 35 (Phase 1: Milestone 1 MVP)

### 1. Objectives
- Acquire real-world Tourism Destination & Attraction Benchmark Dataset into `ml_pipeline/data/raw/`.
- Verify licensing (CC BY-SA 4.0 / ODbL) and compute SHA-256 cryptographic checksums.
- Create automated data loader script with mirror fallback mechanism.
- Execute structural inspection of dimensions, schema, data types, null counts, and duplicate records.
- Validate relational referential integrity across users, places, and interactions.
- Produce `ml_pipeline/DATA_DICTIONARY.md` and `ml_pipeline/notebooks/01_data_inspection.ipynb`.

### 2. Work Completed
- Built `ml_pipeline/src/data_loader.py` with multi-source download resilience and automated checksum verification.
- Downloaded and verified all 3 dataset components:
  - `tourism_with_id.csv` (437 attractions, 13 columns, SHA-256: `f7be2257d5f7007c...`)
  - `tourism_rating.csv` (10,000 rating interactions, 3 columns, SHA-256: `d2c432924f8dcb7e...`)
  - `user.csv` (300 users, 3 columns, SHA-256: `118572535a530f11...`)
- Built `ml_pipeline/src/inspect_data.py` providing automated profiling of null values, duplicates, and category distributions.
- Identified data quality nuances:
  - 2 junk export columns (`Unnamed: 11` with 100% missing values; `Unnamed: 12` numeric index artifact).
  - 232 missing values (53.1%) in `Time_Minutes` duration column.
  - 79 duplicate `(User_Id, Place_Id)` rating events.
  - Confirmed 100% complete and valid geographic coordinates (`Lat`: [-8.1979, 1.0789], `Long`: [103.9314, 112.8217]).
  - Confirmed 100% referential integrity with zero orphan records.
- Authored interactive inspection notebook `ml_pipeline/notebooks/01_data_inspection.ipynb`.
- Authored comprehensive schema specification `ml_pipeline/DATA_DICTIONARY.md`.

### 3. Files Created or Modified
- `ml_pipeline/src/data_loader.py` (Automated dataset acquisition and integrity verification)
- `ml_pipeline/src/inspect_data.py` (Dataset profiling and referential integrity validator)
- `ml_pipeline/notebooks/01_data_inspection.ipynb` (Interactive Jupyter inspection notebook)
- `ml_pipeline/DATA_DICTIONARY.md` (Formal schema, types, distributions, and remediation guidance)
- `DEVELOPMENT_LOG.md` (Updated with Day 2 progress)

### 4. Technical Decisions
- **Deduplication Strategy:** In Day 3 cleaning, the 79 duplicate interactions in `tourism_rating.csv` will be aggregated by arithmetic mean to produce a single deterministic target score per `(User_Id, Place_Id)`.
- **Duration Imputation:** For the 53.1% missing `Time_Minutes`, median category-specific duration will be used to reflect realistic activity pacing.
- **Raw Data Isolation:** Raw CSVs are tracked under `ml_pipeline/data/raw/` with gitignore rules preserving lightweight execution while keeping scripts completely reproducible.

### 5. Problems Encountered
- Primary mirror for `tourism_with_id.csv` returned HTTP 404.

### 6. Solutions Implemented
- The automated data loader utilized secondary verified mirror URLs, completing all downloads with zero manual intervention.

### 7. Tests Performed
- Executed `ml_pipeline/src/data_loader.py` with exit code 0.
- Executed `ml_pipeline/src/inspect_data.py` confirming dimensions (437 places, 10,000 ratings, 300 users) and referential integrity assertions.

### 8. Git Commit Hash
- `6f8715b607c812c68d263c2de130ae8ad662ebdb` (Commit message: `data: acquire and inspect travel dataset`)

### 9. Remaining Tasks
- None for Day 2. Quality Gate 1 fully satisfied.

### 10. Next Day's Objectives (Day 3)
- Implement `ml_pipeline/src/preprocessing.py`.
- Handle missing values (prune junk columns, impute `Time_Minutes` by category median).
- Deduplicate `tourism_rating.csv` interactions.
- Encode categorical features (`Category`, `City`, `Location`).
- Standardize and scale numerical features (`Price`, `Rating`, `Time_Minutes`, `Age`).
- Generate clean, leakage-free train/validation/test splits.
- Save cleaned datasets into `ml_pipeline/data/processed/`.
