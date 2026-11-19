# Database Design Specification — TripSync AI

**Database Engine:** PostgreSQL 15+  
**ORM:** SQLAlchemy 2.0 (Declarative Mapping)  
**Migration Tool:** Alembic  
**Key Strategy:** UUIDv4 Primary Keys, Normalized 3NF Schema, Referential Integrity with Cascade Controls  

---

## 1. Schema Entity-Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ TRIP_MEMBERS : participates
    USERS ||--o{ TRIPS : creates
    USERS ||--o{ PREFERENCES : submits
    USERS ||--o{ VOTES : casts
    USERS ||--o{ BUDGET_ITEMS : creates

    TRIPS ||--|{ TRIP_MEMBERS : contains
    TRIPS ||--o{ PREFERENCES : collects
    TRIPS ||--o{ RECOMMENDATIONS : receives
    TRIPS ||--o{ VOTES : conducts
    TRIPS ||--o{ BUDGET_ITEMS : tracks
    TRIPS ||--o{ ITINERARY_DAYS : schedules

    DESTINATIONS ||--o{ ATTRACTIONS : contains
    DESTINATIONS ||--o{ RECOMMENDATIONS : evaluates

    ATTRACTIONS ||--o{ ITINERARY_ITEMS : scheduled
    ITINERARY_DAYS ||--o{ ITINERARY_ITEMS : organizes

    USERS {
        uuid id PK
        string email UK
        string hashed_password
        string full_name
        string avatar_url
        timestamp created_at
        timestamp updated_at
    }

    TRIPS {
        uuid id PK
        string title
        text description
        date start_date
        date end_date
        uuid created_by FK
        string invite_code UK
        string status
        timestamp created_at
        timestamp updated_at
    }

    TRIP_MEMBERS {
        uuid id PK
        uuid trip_id FK
        uuid user_id FK
        string role
        timestamp joined_at
    }

    PREFERENCES {
        uuid id PK
        uuid trip_id FK
        uuid user_id FK
        decimal budget_min
        decimal budget_max
        string pace_preference
        jsonb category_weights
        string dietary_restrictions
        timestamp updated_at
    }

    DESTINATIONS {
        uuid id PK
        string name
        string country
        string state_region
        decimal latitude
        decimal longitude
        decimal avg_cost_per_day
        text description
        jsonb tags
    }

    ATTRACTIONS {
        uuid id PK
        uuid destination_id FK
        string name
        string category
        decimal rating
        decimal cost
        decimal latitude
        decimal longitude
        int estimated_duration_minutes
    }

    RECOMMENDATIONS {
        uuid id PK
        uuid trip_id FK
        uuid destination_id FK
        decimal group_score
        decimal lowest_member_score
        jsonb explanation_breakdown
        int rank
        timestamp generated_at
    }

    VOTES {
        uuid id PK
        uuid trip_id FK
        uuid user_id FK
        string target_type
        uuid target_id
        int vote_value
        timestamp created_at
    }

    BUDGET_ITEMS {
        uuid id PK
        uuid trip_id FK
        uuid created_by FK
        string category
        string title
        decimal estimated_cost
        decimal actual_cost
        string split_method
        timestamp created_at
    }

    ITINERARY_DAYS {
        uuid id PK
        uuid trip_id FK
        int day_number
        date date
    }

    ITINERARY_ITEMS {
        uuid id PK
        uuid itinerary_day_id FK
        uuid attraction_id FK
        time start_time
        time end_time
        int sort_order
        text notes
    }
```

---

## 2. Table Specifications & Invariants

### 2.1 Identity & Collaboration
- **`users`:** Stores authentication credentials and user profiles. 
  - *Indexes:* Unique index on `email`.
- **`trips`:** Stores group workspaces.
  - *Indexes:* Unique index on `invite_code`, index on `created_by`.
- **`trip_members`:** Junction table for multi-user collaboration.
  - *Constraints:* Unique constraint on `(trip_id, user_id)`. Role enum `('OWNER', 'EDITOR', 'VIEWER')`.
  - *Cascade:* Deleting a trip cascades to delete trip memberships.

### 2.2 Preferences & Surveys
- **`preferences`:** Individual member constraints for a specific trip.
  - *Constraints:* Unique constraint on `(trip_id, user_id)` (one active survey per user per trip).
  - *Fields:* `category_weights` stored as structured JSONB (e.g. `{"nature": 0.8, "culture": 0.4, "adventure": 0.9}`).

### 2.3 Catalog (Destinations & Attractions)
- **`destinations`:** Regional tourism clusters (e.g., Yogyakarta, Bali, Kyoto).
  - *Indexes:* B-Tree index on `(latitude, longitude)` for spatial filtering.
- **`attractions`:** Points of interest associated with a destination.
  - *Indexes:* Foreign key index on `destination_id`, category index.

### 2.4 Decision & Execution
- **`recommendations`:** AI output snapshots for a trip.
  - *Fields:* Stores group score, minimum individual score (least misery), and ranking.
- **`votes`:** User ballots on destinations or attractions.
  - *Constraints:* Unique constraint on `(trip_id, user_id, target_type, target_id)`.
- **`budget_items` & `itinerary_days` / `itinerary_items`:** Group planning execution records with cascade deletes on trip deletion.
