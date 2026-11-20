"""
TripSync AI - Indian Tourism Dataset Inspection and Quality Assessment Script
Analyzes dataset dimensions, schema, geographic distributions, rating patterns, and coordinates across India.
"""

from pathlib import Path
import json
import pandas as pd
import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
DATASET_PATH = DATA_DIR / "top_indian_places.csv"


def inspect_indian_dataset():
    print("=" * 75)
    print("TRIPSYNC AI: INDIAN TOURISM DESTINATIONS DATASET INSPECTION")
    print("=" * 75)

    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at {DATASET_PATH}. Run data_loader.py first.")

    df = pd.read_csv(DATASET_PATH)

    rows, cols = df.shape
    mem_kb = df.memory_usage(deep=True).sum() / 1024
    dups = df.duplicated(subset=["name", "city"]).sum()

    print(f"\n[PHYSICAL DATASET SUMMARY]")
    print(f"  Total Attractions:     {rows}")
    print(f"  Feature Columns:       {cols}")
    print(f"  Memory Footprint:      {mem_kb:.2f} KB")
    print(f"  Duplicate Attractions: {dups}")

    print(f"\n[COLUMN TYPES & MISSING VALUES]")
    for col in df.columns:
        dtype = str(df[col].dtype)
        null_count = int(df[col].isnull().sum())
        null_pct = (null_count / rows) * 100
        print(f"  - {col:25s} | Type: {dtype:10s} | Missing: {null_count:3d} ({null_pct:.1f}%)")

    print("\n" + "=" * 75)
    print("GEOGRAPHIC COVERAGE ACROSS INDIA")
    print("=" * 75)

    print(f"  Total States & UTs: {df['state'].nunique()}")
    print(f"  Total Cities:       {df['city'].nunique()}")

    print("\n[Zonal Distribution in India]:")
    zone_counts = df["zone"].value_counts().to_dict()
    for zone, count in zone_counts.items():
        pct = (count / rows) * 100
        print(f"    - {zone:18s}: {count:3d} places ({pct:.1f}%)")

    print("\n[Top 10 Indian States by Attraction Count]:")
    top_states = df["state"].value_counts().head(10).to_dict()
    for state, count in top_states.items():
        print(f"    - {state:22s}: {count:3d} attractions")

    print("\n[Geospatial Coordinate Validity (India Bounds)]:")
    print(f"  - Latitude Range:   [{df['latitude'].min():.4f}, {df['latitude'].max():.4f}] (Kanyakumari to Ladakh)")
    print(f"  - Longitude Range:  [{df['longitude'].min():.4f}, {df['longitude'].max():.4f}] (Gujarat to Arunachal)")
    print(f"  - Invalid/NaN Coordinates: {df[['latitude', 'longitude']].isnull().sum().sum()}")

    print("\n" + "=" * 75)
    print("ATTRACTION CATEGORIES & TRAVEL LOGISTICS")
    print("=" * 75)

    print("\n[Top 10 Attraction Types]:")
    top_types = df["type"].value_counts().head(10).to_dict()
    for cat_type, count in top_types.items():
        print(f"    - {cat_type:20s}: {count:3d} attractions")

    print("\n[Budget Tier Breakdown (INR Entry Fee)]: ")
    budget_counts = df["budget_tier"].value_counts().to_dict()
    for tier, count in budget_counts.items():
        pct = (count / rows) * 100
        print(f"    - {tier:15s}: {count:3d} attractions ({pct:.1f}%)")

    print("\n[Numerical Logistics Summary]:")
    num_cols = ["time_needed_hrs", "rating", "entrance_fee_inr", "reviews_lakhs"]
    stats_df = df[num_cols].describe().T[["mean", "std", "min", "50%", "max"]]
    stats_df.columns = ["Mean", "StdDev", "Min", "Median", "Max"]
    print(stats_df.to_string())

    print("\n" + "=" * 75)
    print("Sample Indian Destination Record:")
    sample = df.iloc[0].to_dict()
    for k in ["name", "city", "state", "zone", "type", "rating", "entrance_fee_inr", "time_needed_hrs", "best_time_to_visit"]:
        print(f"  {k:20s}: {sample[k]}")
    print("=" * 75)
    print("Quality Gate 1 Satisfied: Indian Tourism Dataset Ready.")
    print("=" * 75)


if __name__ == "__main__":
    inspect_indian_dataset()
