# Project Requirements Document (PRD) — TripSync AI

**Document Version:** 1.0.0  
**Status:** Approved Architectural Baseline  
**Project Horizon:** 35 Days (Phase 1: Days 1–18; Phase 2: Days 19–35)  

---

## 1. Executive Summary & Problem Scope
Planning group travel is an exercise in multi-stakeholder consensus building with heterogeneous constraints:
1. **Financial Heterogeneity:** Unequal willingness or ability to spend across accommodation, food, and activities.
2. **Preference Divergence:** Disparate affinity for pacing, cultural immersion, nightlife, nature, and adventure.
3. **Consensus Bottlenecks:** Lack of objective aggregation mechanisms leads to decision paralysis, disproportionate influence by vocal participants, or group churn.

TripSync AI provides an automated, mathematically sound group travel workspace that bridges individual preference profiles with collective utility optimization.

---

## 2. Functional Requirements (FR)

### FR-1: Identity & Authentication
- **FR-1.1:** Secure registration and authentication using email and strong password validation.
- **FR-1.2:** Password hashing using Argon2id with salted cryptographic security.
- **FR-1.3:** Stateless session management via short-lived JSON Web Tokens (JWT) with secure claims.
- **FR-1.4:** User profile management (name, email, avatar URL, home location, travel style tags).

### FR-2: Group Trip Management & Workspace
- **FR-2.1:** Authenticated users can create trips with destination bounds, date ranges, and descriptions.
- **FR-2.2:** Trip creator is automatically assigned the `Owner` role.
- **FR-2.3:** Secure, cryptographically unguessable alphanumeric invitation links/codes for group onboarding.
- **FR-2.4:** Member role management: `Owner` (full administration), `Editor` (modify plans, submit preferences, vote), `Viewer` (read-only inspection).
- **FR-2.5:** Trip workspace displaying member roster, preference completion status, and active planning stages.

### FR-3: Multi-Participant Preference Survey Engine
- **FR-3.1:** Dynamic, structured preference submission form per member for each trip.
- **FR-3.2:** Explicit inputs collected:
  - Budget range (minimum and maximum acceptable per-person spend).
  - Pacing preference (Relaxed, Moderate, Fast-paced/Intense).
  - Categorical affinity weights (Culture/History, Nature, Adventure, Urban/Nightlife, Relaxation/Beach) on a standardized Likert scale.
  - Dietary requirements and physical accessibility flags.
- **FR-3.3:** Real-time visibility into which group members have submitted or updated their preferences.

### FR-4: AI-Powered Destination & POI Recommendation
- **FR-4.1:** Integration with an independently testable, serialized machine learning model trained on real-world tourism data.
- **FR-4.2:** Computation of individual affinity vectors $\mathbf{\hat{y}}_i$ for all candidate destinations/attractions.
- **FR-4.3:** Execution of the **Group Intelligence Engine** to aggregate individual scores using:
  - **Additive Utilitarianism (Average Satisfaction):** Overall group alignment.
  - **Egalitarian Minimum Satisfaction (Least Misery):** Prevention of severe dissatisfaction for any single member.
  - **Variance & Conflict Detection:** Automatic flagging of polarized options.
- **FR-4.4:** Transparent explainability metadata ("Why this recommendation?": e.g., "High match for Nature lovers; satisfies John's budget constraint").

### FR-5: Collaborative Decision & Voting Module
- **FR-5.1:** Conversion of top AI recommendations into active group voting ballots.
- **FR-5.2:** Support for Approval Voting and Ranked Choice Voting across candidate destinations and attractions.
- **FR-5.3:** Transparent aggregation of votes with visual result summaries, leading to confirmed trip destinations.

### FR-6: Budget Planning & Cost Distribution
- **FR-6.1:** Categorized budget tracking: Accommodation, Transportation, Food & Dining, Activities, Contingency.
- **FR-6.2:** Cost estimation engine comparing group budget bounds against empirical destination price tiers.
- **FR-6.3:** Per-person expense allocation calculator (Equal split, weighted split, or pay-own-way).

### FR-7: Spatial Itinerary Generation & Interactive Mapping
- **FR-7.1:** Automated day-wise itinerary clustering grouping attractions by geographical proximity (Haversine distance) and operating duration.
- **FR-7.2:** Interactive Leaflet.js map rendering pinned destinations, attraction markers, and day-wise route lines using OpenStreetMap tiles.
- **FR-7.3:** Interactive drag-and-drop or reordering capability for group editors.

---

## 3. Non-Functional Requirements (NFR)

### NFR-1: Cost Constraint (Strict Zero-Cost ₹0)
- The application must operate strictly within verified free-tier limits without incurring cloud service charges:
  - Backend compute: Render Free Web Service (512 MB RAM, 0.1 vCPU).
  - Frontend hosting: Cloudflare Pages (unlimited bandwidth).
  - Database: Supabase Free Tier (PostgreSQL 15, 500 MB storage).
- Architectural memory consumption must strictly remain under 400 MB to avoid Render OOM kills.

### NFR-2: Performance & Latency
- P95 API response times for standard CRUD operations under 250 ms.
- Batch ML inference and group aggregation latency for a 10-member group across 50 candidate attractions under 1,200 ms.
- Client-side initial bundle size (gzipped) under 350 KB.

### NFR-3: Security & Privacy
- Zero credential exposure in frontend bundles or public repositories.
- OWASP Top 10 compliance: Strict input validation via Pydantic v2, parameterized SQL queries via SQLAlchemy 2.0 ORM, strict CORS policies, and rate-limiting middleware.
- Object-level authorization enforcing membership verification on every trip-scoped API call.

### NFR-4: Architectural Maintainability & Portability
- Modular Monolith design with explicit domain service interfaces.
- Zero vendor lock-in: Database access adheres to standard PostgreSQL SQL-dialect; containerized via Docker for portable hosting migration.
- Fully automated CI pipeline verifying linting, type-checking, and test suites prior to deployment.

---

## 4. Engineering Quality Gates

| Gate ID | Verification Stage | Mandatory Passing Criteria |
| :--- | :--- | :--- |
| **Gate 1** | **Pre-ML Training (Day 2)** | Dataset license verified, schema validated, leakage-free preprocessing pipeline designed. |
| **Gate 2** | **Pre-Model Integration (Day 7)** | Baseline evaluated, alternative models compared, offline metrics (RMSE, NDCG@K) documented, artifact serialized with metadata. |
| **Gate 3** | **Pre-MVP Deployment (Day 18)** | End-to-end integration verified locally (Auth -> Trip -> Survey -> ML -> Vote -> Budget -> Itinerary), test suite passing, public deployment healthy. |
| **Gate 4** | **Pre-Production Release (Day 35)** | Security audit completed, authorization hardened, query performance profiled, automated CI/CD active, zero high-severity vulnerabilities. |
