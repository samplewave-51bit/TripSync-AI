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
