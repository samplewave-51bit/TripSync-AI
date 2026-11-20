# Data Dictionary & Schema Specification — TripSync AI

**Document Version:** 3.0.0 (India Tourism Baseline)  
**Status:** Validated Raw Data Baseline (Gate 1 Passed)  
**Dataset Name:** Top Indian Places to Visit (Indian Tourism Guide)  
**Source:** Open Data / Kaggle (`saketk511/travel-dataset-guide-to-indias-must-see-places`)  
**Scope:** 325 Premier Tourist Attractions across 33 States and 214 Cities in India  

---

## 1. File Catalog & Physical Attributes

| File Name | Physical Size | Dimensions | Record Granularity | Natural Key | Missing Values | SHA-256 Checksum |
| :--- | :---: | :---: | :--- | :--- | :---: | :--- |
| **`top_indian_places.csv`** | 42.50 KB | 325 rows × 18 cols | Individual Tourist Attraction / Destination in India | `place_id` (Integer) | **0 (0.0%)** | `202ec9d6e0ae1b0c...` |

---

## 2. Comprehensive Column Definitions

| Column Name | Inferred Type | Target DB Type | Null Count (%) | Unique Values | Value Domain & Range | Semantic Description |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **`place_id`** | `int64` | INTEGER | 0 (0.0%) | 325 | [1, 325] | Unique numeric identifier for each attraction. |
| **`name`** | `string` | VARCHAR(255) | 0 (0.0%) | 323 | Taj Mahal, Red Fort, Arambol Beach, Pangong Tso, etc. | Name of the tourist landmark / attraction. |
| **`zone`** | `string` | VARCHAR(50) | 0 (0.0%) | 6 | `Southern` (98), `Northern` (89), `Eastern` (45), `Western` (40), `Central` (39), `North Eastern` (14) | Geographic macro-region of India. |
| **`state`** | `string` | VARCHAR(100) | 0 (0.0%) | 33 | Uttar Pradesh (23), Maharashtra (20), Delhi (19), Karnataka (19), Himachal Pradesh (18), Kerala (16), Rajasthan (15), etc. | Indian State or Union Territory. |
| **`city`** | `string` | VARCHAR(100) | 0 (0.0%) | 214 | Delhi, Jaipur, Agra, Manali, Shimla, Panaji, Kochi, Munnar, Varanasi, Rishikesh, Mumbai, etc. | Nearest urban hub / tourist cluster. |
| **`type`** | `string` | VARCHAR(50) | 0 (0.0%) | 38 | Temple (59), Beach (25), Fort (22), Lake (16), National Park (14), Palace (12), Museum (11), Waterfall (11), Cave (8), Trek, etc. | Primary activity / attraction taxonomy. |
| **`time_needed_hrs`** | `float64` | NUMERIC(3,1) | 0 (0.0%) | 12 | [0.5, 7.0], Mean = 1.81 hrs, Median = 1.5 hrs | Average time required by visitors to explore the venue. |
| **`rating`** | `float64` | NUMERIC(3,1) | 0 (0.0%) | 24 | [1.4, 4.9], Mean = 4.49, Median = 4.5 | Google review rating score benchmark. |
| **`entrance_fee_inr`** | `int64` | INTEGER | 0 (0.0%) | 38 | [₹0, ₹7,500], Mean = ₹115.8, Median = ₹0 | Official entrance fee / ticket price in Indian Rupees (₹). |
| **`reviews_lakhs`** | `float64` | NUMERIC(5,2) | 0 (0.0%) | 55 | [0.01, 7.4], Mean = 0.41 lakhs (41,000 reviews) | Review count in lakhs, representing empirical consumer popularity. |
| **`airport_within_50km`** | `string` | VARCHAR(10) | 0 (0.0%) | 2 | `Yes` (62.2%), `No` (37.8%) | Accessibility indicator for flight connectivity. |
| **`weekly_off`** | `string` | VARCHAR(50) | 0 (0.0%) | 7 | `Open All Days` (90.2%), `Monday`, `Friday`, etc. | Venue operating day restrictions for itinerary scheduling. |
| **`significance`** | `string` | VARCHAR(50) | 0 (0.0%) | 10 | `Historical`, `Religious`, `Nature`, `Adventure`, `Cultural`, `Artistic` | Core cultural or experiential driver. |
| **`dslr_allowed`** | `string` | VARCHAR(10) | 0 (0.0%) | 2 | `Yes` (94.5%), `No` (5.5%) | Photography permission flag. |
| **`best_time_to_visit`** | `string` | VARCHAR(50) | 0 (0.0%) | 5 | `All Day`, `Morning`, `Afternoon`, `Evening` | Optimal time of day for itinerary slotting. |
| **`budget_tier`** | `string` | VARCHAR(20) | 0 (0.0%) | 3 | `Budget` (83.4%, fee <= ₹50), `Mid-range` (12.3%, ₹51–₹500), `Luxury` (4.3%, > ₹500) | Financial accessibility tier. |
| **`latitude`** | `float64` | NUMERIC(9,6) | 0 (0.0%) | 214 | [8.0883, 34.6863] (Kanyakumari to Ladakh) | WGS84 Geographic Latitude. Ready for Leaflet maps. |
| **`longitude`** | `float64` | NUMERIC(9,6) | 0 (0.0%) | 214 | [68.9685, 94.6425] (Gujarat to Arunachal) | WGS84 Geographic Longitude. Ready for Leaflet maps. |

---

## 3. Data Quality Findings & Remediation Strategy (Day 3)

1. **Duplicate Attractions:**
   - Exactly 2 duplicate pairs detected:
     - `Thiksey Monastery` (Leh, Ladakh)
     - `Ramanathaswamy Temple` (Rameswaram, Tamil Nadu)
   - Remediation: Deduplicate by retaining the maximum rating / latest record during Day 3 cleaning.
2. **Category Harmonization:**
   - 38 distinct fine-grained types can be grouped into 5 macro group preference clusters:
     - **Heritage & Culture:** Fort, Palace, Tomb, Monument, Historical Site.
     - **Nature & Scenic:** Lake, Waterfall, Hill, Valley, Beach, Garden.
     - **Spiritual & Religious:** Temple, Mosque, Church, Gurudwara, Monastery.
     - **Adventure & Wildlife:** National Park, Wildlife Sanctuary, Safari, Trek, Cave.
     - **Urban & Modern:** War Memorial, Science Centre, Museum, Amusement Park.
3. **Pacing and Day-Wise Itinerary Integration:**
   - `time_needed_hrs` (0.5 to 7.0 hrs) and `best_time_to_visit` (`Morning`, `Afternoon`, `Evening`) provide realistic constraints for the day-wise itinerary optimization engine without needing synthetic scheduling assumptions.
