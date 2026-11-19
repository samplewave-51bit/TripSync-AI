# System Architecture Document — TripSync AI

**Document Version:** 1.0.0  
**Pattern:** Domain-Centric Modular Monolith  
**Runtime:** Python 3.11 (FastAPI) + React 18 (TypeScript / Vite) + PostgreSQL 15+  

---

## 1. Architectural Strategy & Rationale

TripSync AI employs a **Domain-Centric Modular Monolith**. 

### Why Modular Monolith Over Microservices?
1. **Zero-Cost Constraint (₹0 Budget):** Microservices require multiple container runtimes, API gateways, service meshes, and distributed tracing backends, easily exceeding free-tier resource limits. A modular monolith runs comfortably in a single 512 MB RAM container.
2. **Elimination of Distributed Failure Modes:** Avoids two-phase commits, partial network partitions, and eventual consistency lag across trip planning and voting transactions.
3. **Seamless Future Portability:** Domain boundaries are strictly enforced via decoupled service interfaces and repository layers. If horizontal scale demands service extraction in the future, boundaries already exist without a code rewrite.

---

## 2. Layered Architecture & Boundaries

```mermaid
flowchart TD
    subgraph PresentationLayer ["1. Presentation Layer (SPA)"]
        UI_Components["React Components & Pages"]
        State_Cache["TanStack Query (Client-Side Caching)"]
        HTTP_Client["Axios Interceptor (JWT Auto-Attach)"]
    end

    subgraph APILayer ["2. API & Ingress Layer (FastAPI)"]
        FastAPI_App["FastAPI Entrypoint (app/main.py)"]
        Security_Middleware["Security Headers, CORS & Rate Limiting"]
        Auth_Dependency["get_current_active_user (OAuth2 Bearer)"]
        V1_Router["Master API Router (/api/v1)"]
    end

    subgraph DomainLayer ["3. Core Domain Services (Business Logic)"]
        Auth_Service["AuthService"]
        Trip_Service["TripService"]
        Pref_Service["PreferenceService"]
        ML_Service["RecommendationService"]
        Vote_Service["VotingService"]
        Itin_Service["ItineraryService"]
    end

    subgraph IntelligenceLayer ["4. Analytical & ML Engines"]
        ML_Predictor["TripSyncPredictor (Trained Model)"]
        Group_Engine["GroupIntelligenceEngine (Social Choice)"]
        Spatial_Cluster["SpatialClusteringEngine (Haversine Route)"]
    end

    subgraph DataAccessLayer ["5. Data Access Layer (Repositories)"]
        User_Repo["UserRepository"]
        Trip_Repo["TripRepository"]
        Pref_Repo["PreferenceRepository"]
        Dest_Repo["DestinationRepository"]
        Vote_Repo["VoteRepository"]
    end

    subgraph PersistenceLayer ["6. Storage Layer"]
        Postgres_DB[(Supabase PostgreSQL Database)]
        Model_Artifacts["Serialized Model Artifact (.joblib)"]
    end

    UI_Components --> State_Cache --> HTTP_Client
    HTTP_Client -->|REST / JSON| FastAPI_App
    FastAPI_App --> Security_Middleware --> Auth_Dependency --> V1_Router
    V1_Router --> Auth_Service & Trip_Service & Pref_Service & ML_Service & Vote_Service & Itin_Service
    ML_Service --> ML_Predictor & Group_Engine
    Itin_Service --> Spatial_Cluster
    Auth_Service & Trip_Service & Pref_Service & ML_Service & Vote_Service & Itin_Service --> DataAccessLayer
    DataAccessLayer --> Postgres_DB
    ML_Predictor -.->|Load on Lifespan| Model_Artifacts
```

---

## 3. End-to-End Sequence: Group Recommendation Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Alice as Group Member (Alice)
    actor Bob as Group Member (Bob)
    participant Client as React SPA (Client)
    participant API as FastAPI Router
    participant PrefSvc as PreferenceService
    participant RecSvc as RecommendationService
    participant ML as ML Predictor
    participant GEngine as Group Intelligence Engine
    participant DB as PostgreSQL Database

    Alice->>Client: Fill survey (Budget: $500, Culture: High, Pacing: Relaxed)
    Client->>API: POST /api/v1/trips/{id}/preferences
    API->>PrefSvc: Save Alice's preference
    PrefSvc->>DB: INSERT/UPDATE preferences

    Bob->>Client: Fill survey (Budget: $800, Adventure: High, Pacing: Moderate)
    Client->>API: POST /api/v1/trips/{id}/preferences
    API->>PrefSvc: Save Bob's preference
    PrefSvc->>DB: INSERT/UPDATE preferences

    Alice->>Client: Click "Generate Group Recommendations"
    Client->>API: POST /api/v1/trips/{id}/recommendations/generate
    API->>RecSvc: Trigger recommendation pipeline
    RecSvc->>DB: Fetch group member profiles & candidate destinations
    DB-->>RecSvc: Return [Alice, Bob] preferences & POI candidates
    
    RecSvc->>ML: Vectorize & predict individual affinities
    ML-->>RecSvc: Affinity Matrix (Alice: [POI_A: 4.8, POI_B: 2.1], Bob: [POI_A: 4.2, POI_B: 4.9])
    
    RecSvc->>GEngine: Execute Social Choice Aggregation (Borda + Least Misery)
    GEngine-->>RecSvc: Ranked Group Destinations + Conflict Flags + Explanations
    
    RecSvc->>DB: Persist recommendations & explanation breakdown
    DB-->>RecSvc: Confirmation
    RecSvc-->>API: Return Top-K Ranked Recommendations
    API-->>Client: 200 OK with formatted recommendation cards
    Client-->>Alice: Render recommendations with transparent group compatibility scores
```

---

## 4. In-Memory ML Lifecycle & Resource Discipline

On a free-tier hosting instance with 512 MB RAM (e.g. Render Free), reckless model loading causes unrecoverable Out-Of-Memory (OOM) termination. We enforce the following rules:

1. **Singleton Pre-Warming at Startup:** The serialized model artifact (`model.joblib`, <25 MB) and preprocessor transforms are loaded once during FastAPI's `lifespan` startup event into an in-memory `ModelRegistry`.
2. **Zero Retraining in Web Thread:** The web API only executes feed-forward inference (matrix multiplications and tree traversals). Model retraining happens strictly offline in `ml_pipeline/`.
3. **NumPy Vectorized Inference:** Matrix computations are vectorized across the group rather than iterated through Python for-loops, maintaining inference execution times under 150 ms for a 10-person group across 100 destinations.
