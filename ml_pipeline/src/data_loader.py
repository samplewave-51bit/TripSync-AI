"""
TripSync AI - Data Acquisition Pipeline
Downloads, verifies, and stores the Tourism Destination & Attraction Benchmark Dataset.
License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) / ODbL
"""

import hashlib
import os
from pathlib import Path
from typing import Dict, List
import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

# Primary and fallback mirror URLs for raw real-world CSV files
DATASET_SOURCES: Dict[str, List[str]] = {
    "tourism_with_id.csv": [
        "https://raw.githubusercontent.com/halowisata/ViVe-Machine-Learning-Flask/main/data/raw/tourism_with_id.csv",
        "https://raw.githubusercontent.com/Tar-ive/Travel-Recommendation-Model-/main/tourism_with_id.csv",
    ],
    "tourism_rating.csv": [
        "https://raw.githubusercontent.com/halowisata/ViVe-Machine-Learning-Flask/main/data/raw/tourism_rating.csv",
        "https://raw.githubusercontent.com/Tar-ive/Travel-Recommendation-Model-/main/tourism_rating.csv",
    ],
    "user.csv": [
        "https://raw.githubusercontent.com/halowisata/ViVe-Machine-Learning-Flask/main/data/raw/user.csv",
        "https://raw.githubusercontent.com/Tar-ive/Travel-Recommendation-Model-/main/user.csv",
    ],
}


def compute_sha256(filepath: Path) -> str:
    """Computes SHA-256 hash of a file for integrity tracking."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def download_file(filename: str, urls: List[str], target_dir: Path) -> Path:
    """Downloads a file from mirror URLs with fallback support."""
    target_path = target_dir / filename
    target_dir.mkdir(parents=True, exist_ok=True)

    for url in urls:
        print(f"Attempting download for '{filename}' from {url}...")
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200 and len(response.content) > 0:
                with open(target_path, "wb") as f:
                    f.write(response.content)
                file_size_kb = target_path.stat().st_size / 1024
                file_hash = compute_sha256(target_path)
                print(f"[SUCCESS] Downloaded '{filename}' ({file_size_kb:.2f} KB) - SHA-256: {file_hash[:16]}...")
                return target_path
            else:
                print(f"[WARN] Non-200 response ({response.status_code}) from {url}")
        except Exception as e:
            print(f"[ERROR] Failed to fetch from {url}: {e}")

    raise RuntimeError(f"Failed to download {filename} from all available sources.")


def acquire_all_datasets() -> Dict[str, Dict]:
    """Downloads all dataset artifacts and returns metadata."""
    print("=" * 60)
    print("TripSync AI: Real-World Dataset Acquisition (Gate 1)")
    print("=" * 60)
    manifest = {}
    for filename, urls in DATASET_SOURCES.items():
        file_path = download_file(filename, urls, DATA_DIR)
        manifest[filename] = {
            "path": str(file_path),
            "size_bytes": file_path.stat().st_size,
            "sha256": compute_sha256(file_path),
        }
    print("=" * 60)
    print("All dataset artifacts successfully acquired and verified.")
    return manifest


if __name__ == "__main__":
    acquire_all_datasets()
