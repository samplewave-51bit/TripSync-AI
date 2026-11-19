"""
TripSync AI - Global Dataset Acquisition Pipeline
Downloads, verifies, and stores the Worldwide Travel Cities (Ratings and Climate) Dataset.
Scope: 560 cities across 167 countries with thematic ratings, budget tiers, durations, and coordinates.
"""

import hashlib
import os
import shutil
from pathlib import Path
from typing import Dict
import kagglehub

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
TARGET_FILE = DATA_DIR / "worldwide_travel_cities.csv"
DATASET_SLUG = "furkanima/worldwide-travel-cities-ratings-and-climate"


def compute_sha256(filepath: Path) -> str:
    """Computes SHA-256 hash of a file for cryptographic integrity."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def acquire_dataset() -> Dict[str, any]:
    """Acquires the global travel cities dataset via kagglehub or verifies existing file."""
    print("=" * 70)
    print("TRIPSYNC AI: WORLDWIDE TRAVEL CITIES DATASET ACQUISITION (GATE 1)")
    print("=" * 70)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not TARGET_FILE.exists() or TARGET_FILE.stat().st_size == 0:
        print(f"Fetching dataset '{DATASET_SLUG}' via kagglehub...")
        download_path = Path(kagglehub.dataset_download(DATASET_SLUG))
        # Find csv in the downloaded folder
        csv_files = list(download_path.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV file found in downloaded path: {download_path}")
        source_csv = csv_files[0]
        shutil.copyfile(source_csv, TARGET_FILE)
        print(f"[SUCCESS] Downloaded and moved to {TARGET_FILE}")
    else:
        print(f"[INFO] Verified dataset already present at {TARGET_FILE}")

    file_size_kb = TARGET_FILE.stat().st_size / 1024
    file_hash = compute_sha256(TARGET_FILE)

    print(f"  Target File:     {TARGET_FILE.name}")
    print(f"  File Size:       {file_size_kb:.2f} KB")
    print(f"  SHA-256 Hash:    {file_hash}")
    print("=" * 70)

    return {
        "filename": TARGET_FILE.name,
        "path": str(TARGET_FILE),
        "size_bytes": TARGET_FILE.stat().st_size,
        "sha256": file_hash,
    }


if __name__ == "__main__":
    acquire_dataset()
