# Data Dictionary & Schema Specification — TripSync AI

**Document Version:** 1.0.0  
**Status:** Validated Raw Data Baseline (Gate 1 Passed)  
**Dataset Name:** Tourism Destination & Attraction Benchmark Dataset  
**License:** Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) / ODbL  

---

## 1. File Catalog & Physical Attributes

| File Name | Physical Size | Dimensions | Record Granularity | Primary Key / Natural Key | SHA-256 Checksum (Truncated) |
| :--- | :---: | :---: | :--- | :--- | :--- |
| **`tourism_with_id.csv`** | 357.22 KB | 437 rows × 13 cols | Individual Tourist Attraction / POI | `Place_Id` (Integer) | `f7be2257d5f7007c...` |
| **`tourism_rating.csv`** | 101.58 KB | 10,000 rows × 3 cols | User-Item Rating Event | Composite `(User_Id, Place_Id)` | `d2c432924f8dcb7e...` |
| **`user.csv`** | 9.00 KB | 300 rows × 3 cols | User Demographic Profile | `User_Id` (Integer) | `118572535a530f11...` |

---

## 2. Table Schemas & Feature Metadata

### 2.1 Attractions Catalog (`tourism_with_id.csv`)

| Column Name | Inferred Type | Storage Type | Null Count (%) | Unique Values | Domain & Value Range | Description & Notes |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **`Place_Id`** | `int64` | INTEGER | 0 (0.0%) | 437 | [1, 437] | Unique identifier for each tourist attraction. |
| **`Place_Name`** | `object` / `string` | VARCHAR(255) | 0 (0.0%) | 437 | Text strings | Descriptive title/name of the attraction. |
| **`Description`** | `object` / `string` | TEXT | 0 (0.0%) | 437 | Indonesian prose | Detailed narrative overview of the attraction. |
| **`Category`** | `object` / `string` | VARCHAR(50) | 0 (0.0%) | 6 | Taman Hiburan (135), Budaya (117), Cagar Alam (106), Bahari (47), Tempat Ibadah (17), Pusat Perbelanjaan (15) | Primary thematic classification of the venue. |
| **`City`** | `object` / `string` | VARCHAR(50) | 0 (0.0%) | 5 | Yogyakarta (126), Bandung (124), Jakarta (84), Semarang (57), Surabaya (46) | Urban destination cluster. |
| **`Price`** | `int64` | NUMERIC | 0 (0.0%) | 58 | [0, 900,000 IDR] | Standard ticket / admission price in local currency units. |
| **`Rating`** | `float64` | NUMERIC(3,1) | 0 (0.0%) | 27 | [3.4, 5.0], Mean = 4.44 | Historical average consumer rating benchmark. |
| **`Time_Minutes`**| `float64` | INTEGER | **232 (53.1%)** | 17 | [10, 360], Median = 60 | Average visiting duration in minutes. Requires Day 3 imputation. |
| **`Coordinate`** | `object` / `string` | TEXT | 0 (0.0%) | 437 | Lat/Lng dictionary string | Raw coordinate representation (redundant with Lat/Long). |
| **`Lat`** | `float64` | NUMERIC(9,6) | 0 (0.0%) | 437 | [-8.1979, 1.0789] | WGS84 Geographic Latitude. Ready for Leaflet maps. |
| **`Long`** | `float64` | NUMERIC(9,6) | 0 (0.0%) | 437 | [103.9314, 112.8217] | WGS84 Geographic Longitude. Ready for Leaflet maps. |
| **`Unnamed: 11`**| `float64` | NULL | **437 (100.0%)** | 0 | None | Artifact column from upstream export. To be dropped. |
| **`Unnamed: 12`**| `int64` | INTEGER | 0 (0.0%) | 437 | [0, 436] | Upstream row index artifact. To be dropped. |

---

### 2.2 Interaction Ratings (`tourism_rating.csv`)

| Column Name | Inferred Type | Storage Type | Null Count (%) | Unique Values | Domain & Value Range | Description & Notes |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **`User_Id`** | `int64` | INTEGER | 0 (0.0%) | 300 | [1, 300] | Foreign key referencing `user.csv(User_Id)`. |
| **`Place_Id`** | `int64` | INTEGER | 0 (0.0%) | 437 | [1, 437] | Foreign key referencing `tourism_with_id.csv(Place_Id)`. |
| **`Place_Ratings`**| `int64` | SMALLINT | 0 (0.0%) | 5 | {1: 17.1%, 2: 20.7%, 3: 21.0%, 4: 21.1%, 5: 20.2%} | **Target variable.** Explicit user satisfaction rating. |

---

### 2.3 User Demographics (`user.csv`)

| Column Name | Inferred Type | Storage Type | Null Count (%) | Unique Values | Domain & Value Range | Description & Notes |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **`User_Id`** | `int64` | INTEGER | 0 (0.0%) | 300 | [1, 300] | Primary Key. User identity index. |
| **`Location`** | `object` / `string` | VARCHAR(100) | 0 (0.0%) | 28 | Cities (Semarang, Bekasi, Jakarta, etc.) | User hometown/origin city. |
| **`Age`** | `int64` | SMALLINT | 0 (0.0%) | 23 | [18, 40], Mean = 28.7 years | User age in years. |

---

## 3. Data Quality Findings & Day 3 Remediation Strategy

1. **Junk Columns:** `Unnamed: 11` (100% missing) and `Unnamed: 12` (redundant numeric index) must be pruned during ingestion.
2. **Missing `Time_Minutes` (53.1% missing):**
   - Imputation strategy: Median duration partitioned by `Category` (e.g. amusement parks have longer typical visits than viewpoints).
3. **Duplicate Interactions (79 records in `tourism_rating.csv`):**
   - Exactly 79 duplicate `(User_Id, Place_Id)` rating events exist.
   - Remediation: Aggregate duplicate entries by computing the arithmetic mean rating per `(User_Id, Place_Id)` pair, ensuring a single deterministic target score.
4. **Referential Integrity:** 100% verified. Every interaction maps to an existing attraction and user.
