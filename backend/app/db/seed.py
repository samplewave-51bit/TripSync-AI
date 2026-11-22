"""
TripSync AI - Database Seeder for Indian Tourism Destinations & Attractions
Seeds all 323 verified destinations and points of interest from places_cleaned.csv into PostgreSQL / SQLite.
Idempotent: Safely skips existing place_ids.
"""

import logging
from pathlib import Path
from typing import Dict, Tuple
import pandas as pd
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal, engine
from backend.app.models.base import Base
from backend.app.models.destination import Attraction, Destination

logger = logging.getLogger("TripSyncSeeder")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
PLACES_CSV_PATH = BASE_DIR / "ml_pipeline" / "data" / "processed" / "places_cleaned.csv"


def seed_destinations_and_attractions(db: Session) -> Tuple[int, int]:
    """
    Seeds unique Indian destinations (cities) and all 323 attractions.
    Returns (num_destinations_seeded, num_attractions_seeded).
    """
    if not PLACES_CSV_PATH.exists():
        raise FileNotFoundError(f"Places CSV not found at {PLACES_CSV_PATH}")

    df = pd.read_csv(PLACES_CSV_PATH)
    logger.info(f"Loaded {len(df)} tourist attraction records from {PLACES_CSV_PATH}")

    # 1. Seed or retrieve regional destination clusters (cities)
    destination_map: Dict[Tuple[str, str], Destination] = {}
    dest_seeded = 0

    # Query existing destinations
    existing_dests = db.query(Destination).all()
    for d in existing_dests:
        destination_map[(d.name.lower(), d.state.lower())] = d

    # Group by city and state to establish destination hubs
    city_groups = df.groupby(["city", "state", "zone"]).agg({
        "latitude": "mean",
        "longitude": "mean",
        "type": lambda x: list(set(x))[:5],
    }).reset_index()

    for _, row in city_groups.iterrows():
        key = (str(row["city"]).lower(), str(row["state"]).lower())
        if key not in destination_map:
            dest = Destination(
                name=str(row["city"]),
                state=str(row["state"]),
                zone=str(row["zone"]),
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                avg_cost_per_day=2500.0,
                description=f"Iconic Indian tourism hub in {row['state']} featuring attractions across {', '.join(row['type'])}.",
                tags=list(row["type"]),
            )
            db.add(dest)
            destination_map[key] = dest
            dest_seeded += 1

    db.flush()
    logger.info(f"Processed destinations: {dest_seeded} new hubs created, {len(destination_map)} total available.")

    # 2. Seed all 323 Attractions
    existing_place_ids = {a.place_id for a in db.query(Attraction.place_id).all()}
    attr_seeded = 0

    for _, row in df.iterrows():
        p_id = int(row["place_id"])
        if p_id in existing_place_ids:
            continue

        dest_key = (str(row["city"]).lower(), str(row["state"]).lower())
        dest_obj = destination_map.get(dest_key)

        thematic_vec = {
            "culture_heritage": float(row.get("theme_culture_heritage", 0.0)),
            "nature_wildlife": float(row.get("theme_nature_wildlife", 0.0)),
            "spiritual_religious": float(row.get("theme_spiritual_religious", 0.0)),
            "adventure_outdoor": float(row.get("theme_adventure_outdoor", 0.0)),
            "urban_entertainment": float(row.get("theme_urban_entertainment", 0.0)),
        }

        attraction = Attraction(
            place_id=p_id,
            destination_id=dest_obj.id if dest_obj else None,
            name=str(row["name"]),
            city=str(row["city"]),
            state=str(row["state"]),
            zone=str(row["zone"]),
            type=str(row["type"]),
            rating=float(row["rating"]),
            entrance_fee_inr=float(row["entrance_fee_inr"]),
            time_needed_hrs=float(row["time_needed_hrs"]),
            reviews_lakhs=float(row["reviews_lakhs"]),
            weekly_off=str(row["weekly_off"]),
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            significance=str(row.get("significance", "Iconic tourist destination")),
            dslr_allowed=bool(row.get("dslr_allowed", "yes") == "yes"),
            best_time_to_visit=str(row.get("best_time_to_visit", "All Day")),
            budget_tier=str(row.get("budget_tier", "Budget")),
            macro_category=str(row.get("macro_category", "culture_heritage")),
            thematic_vectors=thematic_vec,
        )
        db.add(attraction)
        existing_place_ids.add(p_id)
        attr_seeded += 1

    db.commit()
    logger.info(f"Successfully seeded {attr_seeded} attractions into database. Total in catalog: {len(existing_place_ids)}.")
    return dest_seeded, attr_seeded


def main():
    """Initializes tables and seeds data."""
    logger.info("Ensuring database schema exists...")
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        dest_count, attr_count = seed_destinations_and_attractions(db)
        logger.info(f"Seed complete: {dest_count} destinations, {attr_count} attractions.")


if __name__ == "__main__":
    main()
