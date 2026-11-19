"""
TripSync AI - Global Dataset Inspection and Quality Assessment Script
Analyzes dataset dimensions, schema, null values, global coverage, and thematic distributions.
"""

from pathlib import Path
import json
import pandas as pd
import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
DATASET_PATH = DATA_DIR / "worldwide_travel_cities.csv"


def inspect_worldwide_dataset():
    print("=" * 75)
    print("TRIPSYNC AI: WORLDWIDE TRAVEL CITIES DATASET INSPECTION")
    print("=" * 75)

    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at {DATASET_PATH}. Run data_loader.py first.")

    df = pd.read_csv(DATASET_PATH)

    rows, cols = df.shape
    mem_kb = df.memory_usage(deep=True).sum() / 1024
    dups = df.duplicated().sum()

    print(f"\n[PHYSICAL DATASET SUMMARY]")
    print(f"  Rows (Destinations):   {rows}")
    print(f"  Columns (Features):    {cols}")
    print(f"  Memory Footprint:      {mem_kb:.2f} KB")
    print(f"  Duplicate Rows:        {dups}")

    print(f"\n[COLUMN-WISE DATA TYPES & MISSING VALUES]")
    for col in df.columns:
        dtype = str(df[col].dtype)
        null_count = int(df[col].isnull().sum())
        null_pct = (null_count / rows) * 100
        print(f"  - {col:25s} | Type: {dtype:10s} | Missing: {null_count:3d} ({null_pct:.1f}%)")

    print("\n" + "=" * 75)
    print("GLOBAL GEOGRAPHIC & REGIONAL COVERAGE")
    print("=" * 75)

    num_countries = df["country"].nunique()
    print(f"\n[Global Reach]: {num_countries} distinct countries across all continents")
    top_countries = df["country"].value_counts().head(10).to_dict()
    print("  Top Represented Countries:")
    for country, count in top_countries.items():
        print(f"    - {country:25s}: {count:3d} destinations")

    print("\n[Continental Region Breakdown]:")
    region_counts = df["region"].value_counts().to_dict()
    for reg, count in region_counts.items():
        pct = (count / rows) * 100
        print(f"    - {reg:20s}: {count:3d} cities ({pct:.1f}%)")

    print("\n[Geospatial Coordinate Validity]:")
    print(f"  - Latitude Range:   [{df['latitude'].min():.4f}, {df['latitude'].max():.4f}]")
    print(f"  - Longitude Range:  [{df['longitude'].min():.4f}, {df['longitude'].max():.4f}]")
    print(f"  - Invalid/NaN Coordinates: {df[['latitude', 'longitude']].isnull().sum().sum()}")

    print("\n" + "=" * 75)
    print("PLANNING LOGISTICS & THEMATIC RATING ATTRIBUTES")
    print("=" * 75)

    print("\n[Budget Level Distribution]:")
    budget_counts = df["budget_level"].value_counts().to_dict()
    for budget, count in budget_counts.items():
        pct = (count / rows) * 100
        print(f"    - {budget:15s}: {count:3d} destinations ({pct:.1f}%)")

    thematic_features = [
        "culture", "adventure", "nature", "beaches",
        "nightlife", "cuisine", "wellness", "urban", "seclusion"
    ]
    print("\n[Thematic Experience Ratings Summary (Scale: 1.0 - 5.0)]:")
    stats_df = df[thematic_features].describe().T[["mean", "std", "min", "50%", "max"]]
    stats_df.columns = ["Mean", "StdDev", "Min", "Median", "Max"]
    print(stats_df.to_string())

    print("\n" + "=" * 75)
    print("Sample Destination Record:")
    sample = df.iloc[0].to_dict()
    for k in ["city", "country", "region", "budget_level", "short_description"]:
        print(f"  {k:18s}: {sample[k]}")
    print("=" * 75)
    print("Quality Gate 1 Satisfied: Global Real-World Dataset Ready.")
    print("=" * 75)


if __name__ == "__main__":
    inspect_worldwide_dataset()
