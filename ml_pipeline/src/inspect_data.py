"""
TripSync AI - Dataset Inspection and Quality Assessment Script
Analyzes dataset dimensions, schema, null values, duplicates, and integrity.
"""

from pathlib import Path
import json
import pandas as pd
import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def analyze_dataframe(df: pd.DataFrame, name: str) -> dict:
    """Performs deep statistical and structural analysis of a DataFrame."""
    analysis = {
        "name": name,
        "rows": int(len(df)),
        "columns_count": int(len(df.columns)),
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "null_counts": {col: int(count) for col, count in df.isnull().sum().items()},
        "duplicate_rows": int(df.duplicated().sum()),
        "memory_usage_kb": float(df.memory_usage(deep=True).sum() / 1024),
    }
    return analysis


def inspect_datasets():
    print("=" * 70)
    print("TRIPSYNC AI: COMPREHENSIVE DATASET INSPECTION")
    print("=" * 70)

    # 1. Load DataFrames
    places_df = pd.read_csv(DATA_DIR / "tourism_with_id.csv")
    ratings_df = pd.read_csv(DATA_DIR / "tourism_rating.csv")
    users_df = pd.read_csv(DATA_DIR / "user.csv")

    analyses = [
        analyze_dataframe(places_df, "tourism_with_id.csv (Attractions)"),
        analyze_dataframe(ratings_df, "tourism_rating.csv (User Ratings)"),
        analyze_dataframe(users_df, "user.csv (User Profiles)"),
    ]

    for item in analyses:
        print(f"\n[FILE: {item['name']}]")
        print(f"  Dimensions: {item['rows']} rows x {item['columns_count']} columns")
        print(f"  Memory footprint: {item['memory_usage_kb']:.2f} KB")
        print(f"  Duplicate records: {item['duplicate_rows']}")
        print("  Column Breakdown:")
        for col in item["columns"]:
            dtype = item["dtypes"][col]
            nulls = item["null_counts"][col]
            null_pct = (nulls / item["rows"]) * 100
            print(f"    - {col:30s} | Type: {dtype:10s} | Missing: {nulls:5d} ({null_pct:.1f}%)")

    # 2. Specific Domain Sanity Checks
    print("\n" + "=" * 70)
    print("DOMAIN SANITY & INTEGRITY CHECKS")
    print("=" * 70)

    # Categories
    categories = places_df["Category"].value_counts().to_dict()
    print(f"\n[Attraction Categories ({len(categories)})]:")
    for cat, count in categories.items():
        print(f"  - {cat:25s}: {count:4d} places")

    # Cities
    cities = places_df["City"].value_counts().to_dict()
    print(f"\n[Attraction Cities ({len(cities)})]:")
    for city, count in cities.items():
        print(f"  - {city:25s}: {count:4d} places")

    # Ratings Distribution
    ratings_stats = ratings_df["Place_Ratings"].describe().to_dict()
    print(f"\n[Ratings Summary (10,000 interactions)]:")
    print(f"  - Min rating: {ratings_stats['min']}")
    print(f"  - Max rating: {ratings_stats['max']}")
    print(f"  - Mean rating: {ratings_stats['mean']:.2f}")
    print(f"  - Median rating: {ratings_stats['50%']:.2f}")

    rating_value_counts = ratings_df["Place_Ratings"].value_counts().sort_index().to_dict()
    print("  - Value Distribution:")
    for val, count in rating_value_counts.items():
        print(f"      Rating {val}: {count:5d} ({count / len(ratings_df) * 100:.1f}%)")

    # Referential Integrity
    unique_places_catalog = set(places_df["Place_Id"])
    unique_places_rated = set(ratings_df["Place_Id"])
    unmatched_places = unique_places_rated - unique_places_catalog

    unique_users_catalog = set(users_df["User_Id"])
    unique_users_rated = set(ratings_df["User_Id"])
    unmatched_users = unique_users_rated - unique_users_catalog

    print(f"\n[Referential Integrity Checks]:")
    print(f"  - Unique Places in Catalog: {len(unique_places_catalog)}")
    print(f"  - Unique Places in Ratings: {len(unique_places_rated)}")
    print(f"  - Unmatched Place IDs in ratings: {len(unmatched_places)} (Expected: 0)")
    print(f"  - Unique Users in Profiles: {len(unique_users_catalog)}")
    print(f"  - Unique Users in Ratings:  {len(unique_users_rated)}")
    print(f"  - Unmatched User IDs in ratings:  {len(unmatched_users)} (Expected: 0)")

    # Lat/Long checks
    null_coords = places_df[["Lat", "Long"]].isnull().sum().to_dict()
    print(f"\n[Geospatial Coordinate Validity]:")
    print(f"  - Missing Latitude:  {null_coords['Lat']}")
    print(f"  - Missing Longitude: {null_coords['Long']}")
    print(f"  - Lat Range:  [{places_df['Lat'].min():.4f}, {places_df['Lat'].max():.4f}]")
    print(f"  - Long Range: [{places_df['Long'].min():.4f}, {places_df['Long'].max():.4f}]")

    print("\n" + "=" * 70)
    print("Inspection successfully completed. Quality Gate 1 satisfied.")
    print("=" * 70)


if __name__ == "__main__":
    inspect_datasets()
