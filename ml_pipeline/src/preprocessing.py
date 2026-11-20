"""
TripSync AI - Data Cleaning & Preprocessing Pipeline
Transforms raw Indian tourism dataset into model-ready, leakage-free feature representations.
Deliverables: places_cleaned.csv, train.parquet, val.parquet, test.parquet, preprocessor.joblib
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, StandardScaler

ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = ROOT_DIR / "data" / "raw" / "top_indian_places.csv"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"

# 5 Thematic Macro-Categories for Group Preference Survey Matching
MACRO_CATEGORY_MAP: Dict[str, str] = {
    # 1. Culture & Heritage
    "Fort": "culture_heritage",
    "Palace": "culture_heritage",
    "Tomb": "culture_heritage",
    "Monument": "culture_heritage",
    "Historical Site": "culture_heritage",
    "War Memorial": "culture_heritage",
    "Stepwell": "culture_heritage",
    # 2. Nature & Scenic Landscapes
    "Lake": "nature_wildlife",
    "Waterfall": "nature_wildlife",
    "Valley": "nature_wildlife",
    "Hill": "nature_wildlife",
    "Garden": "nature_wildlife",
    "National Park": "nature_wildlife",
    "Wildlife Sanctuary": "nature_wildlife",
    "Mangrove": "nature_wildlife",
    "River": "nature_wildlife",
    # 3. Spiritual & Religious Landmarks
    "Temple": "spiritual_religious",
    "Monastery": "spiritual_religious",
    "Mosque": "spiritual_religious",
    "Church": "spiritual_religious",
    "Gurudwara": "spiritual_religious",
    "Ashram": "spiritual_religious",
    "Pilgrimage Site": "spiritual_religious",
    # 4. Adventure & Outdoor Activities
    "Beach": "adventure_outdoor",
    "Trek": "adventure_outdoor",
    "Cave": "adventure_outdoor",
    "Pass": "adventure_outdoor",
    "Skiing": "adventure_outdoor",
    "Water Sports": "adventure_outdoor",
    "Desert": "adventure_outdoor",
    # 5. Urban, Educational & Modern Entertainment
    "Museum": "urban_entertainment",
    "Science Centre": "urban_entertainment",
    "Amusement Park": "urban_entertainment",
    "Observatory": "urban_entertainment",
    "Market": "urban_entertainment",
    "Aquarium": "urban_entertainment",
}


def load_raw_data() -> pd.DataFrame:
    """Loads raw dataset and validates initial existence."""
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Raw dataset not found at {RAW_DATA_PATH}. Run data_loader.py first.")
    return pd.read_csv(RAW_DATA_PATH)


def clean_and_normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans inconsistencies, removes duplicate attractions, and normalizes strings."""
    print("[1/5] Cleaning raw records and eliminating duplicates...")
    initial_count = len(df)

    # 1. Clean string fields
    string_cols = ["name", "zone", "state", "city", "type", "significance", "weekly_off", "best_time_to_visit"]
    for col in string_cols:
        df[col] = df[col].astype(str).str.strip()

    # 2. Fix state naming typos
    state_fixes = {
        "Maharastra": "Maharashtra",
        "Tamilnadu": "Tamil Nadu",
        "Orissa": "Odisha",
    }
    df["state"] = df["state"].replace(state_fixes)

    # 3. Deduplicate on (name, city) keeping record with higher reviews / rating
    df = df.sort_values(by=["rating", "reviews_lakhs"], ascending=False)
    df = df.drop_duplicates(subset=["name", "city"], keep="first")
    df = df.sort_values(by="place_id").reset_index(drop=True)

    pruned = initial_count - len(df)
    print(f"      Removed {pruned} duplicate attraction entries. Clean total: {len(df)}")
    return df


def engineer_thematic_vectors(df: pd.DataFrame) -> pd.DataFrame:
    """Maps fine-grained types into 5 standardized macro-experience columns."""
    print("[2/5] Engineering 5-dimensional thematic experience vectors...")

    # Assign macro category
    def map_macro(raw_type: str) -> str:
        for key, macro in MACRO_CATEGORY_MAP.items():
            if key.lower() in raw_type.lower():
                return macro
        return "culture_heritage"  # default fallback

    df["macro_category"] = df["type"].apply(map_macro)

    # Build binary/affinity indicator features for each macro dimension
    macro_dimensions = [
        "culture_heritage",
        "nature_wildlife",
        "spiritual_religious",
        "adventure_outdoor",
        "urban_entertainment",
    ]

    for dim in macro_dimensions:
        df[f"theme_{dim}"] = (df["macro_category"] == dim).astype(float)

    # Ordinal budget encoding
    budget_map = {"Budget": 0, "Mid-range": 1, "Luxury": 2}
    df["budget_tier_code"] = df["budget_tier"].map(budget_map).fillna(0).astype(int)

    # Binary flags
    df["has_airport_50km"] = (df["airport_within_50km"].str.lower() == "yes").astype(int)
    df["is_dslr_allowed"] = (df["dslr_allowed"].str.lower() == "yes").astype(int)

    # Log-transformed continuous values to handle high-skew distributions
    df["log_entrance_fee"] = np.log1p(df["entrance_fee_inr"].clip(lower=0))
    df["log_reviews"] = np.log1p(df["reviews_lakhs"].clip(lower=0))

    return df


def build_and_fit_preprocessor(train_df: pd.DataFrame) -> Tuple[ColumnTransformer, List[str]]:
    """Constructs a scikit-learn ColumnTransformer fitted exclusively on training data."""
    print("[3/5] Fitting ColumnTransformer on training split to guarantee zero data leakage...")

    numeric_minmax_features = ["time_needed_hrs", "latitude", "longitude"]
    numeric_standard_features = ["log_entrance_fee", "log_reviews", "budget_tier_code"]
    categorical_onehot_features = ["zone", "best_time_to_visit"]
    passthrough_features = [
        "theme_culture_heritage",
        "theme_nature_wildlife",
        "theme_spiritual_religious",
        "theme_adventure_outdoor",
        "theme_urban_entertainment",
        "has_airport_50km",
        "is_dslr_allowed",
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num_minmax", MinMaxScaler(), numeric_minmax_features),
            ("num_standard", StandardScaler(), numeric_standard_features),
            ("cat_onehot", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"), categorical_onehot_features),
            ("pass", "passthrough", passthrough_features),
        ],
        remainder="drop",
    )

    preprocessor.fit(train_df)

    # Extract transformed feature names
    cat_encoder = preprocessor.named_transformers_["cat_onehot"]
    cat_names = list(cat_encoder.get_feature_names_out(categorical_onehot_features))
    feature_names = numeric_minmax_features + numeric_standard_features + cat_names + passthrough_features

    return preprocessor, feature_names


def run_pipeline() -> Dict[str, any]:
    """Executes the complete preprocessing pipeline, creating clean data and split artifacts."""
    print("=" * 75)
    print("TRIPSYNC AI: DATA CLEANING & LEAKAGE-FREE PREPROCESSING PIPELINE")
    print("=" * 75)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load & Clean
    df_raw = load_raw_data()
    df_clean = clean_and_normalize(df_raw)
    df_engineered = engineer_thematic_vectors(df_clean)

    # Save full clean reference table (CSV)
    clean_csv_path = PROCESSED_DIR / "places_cleaned.csv"
    df_engineered.to_csv(clean_csv_path, index=False)
    print(f"      Saved comprehensive cleaned dataset: {clean_csv_path.name}")

    # 2. Split into Train (80%), Validation (10%), Test (10%)
    print("[4/5] Partitioning dataset into 80% Train, 10% Validation, 10% Test (Seed: 42)...")
    train_df, test_val_df = train_test_split(df_engineered, test_size=0.20, random_state=42, shuffle=True)
    val_df, test_df = train_test_split(test_val_df, test_size=0.50, random_state=42, shuffle=True)

    print(f"      Train set:      {len(train_df)} samples ({len(train_df)/len(df_engineered)*100:.1f}%)")
    print(f"      Validation set: {len(val_df)} samples ({len(val_df)/len(df_engineered)*100:.1f}%)")
    print(f"      Test set:       {len(test_df)} samples ({len(test_df)/len(df_engineered)*100:.1f}%)")

    # 3. Fit Preprocessor ONLY on Train set
    preprocessor, feature_names = build_and_fit_preprocessor(train_df)

    # Transform all three splits
    X_train_trans = preprocessor.transform(train_df)
    X_val_trans = preprocessor.transform(val_df)
    X_test_trans = preprocessor.transform(test_df)

    # Create DataFrames with transformed feature names and preserve metadata
    def build_split_df(source_df: pd.DataFrame, X_trans: np.ndarray) -> pd.DataFrame:
        features_df = pd.DataFrame(X_trans, columns=feature_names, index=source_df.index)
        features_df["target_rating"] = source_df["rating"].values
        features_df["place_id"] = source_df["place_id"].values
        features_df["name"] = source_df["name"].values
        features_df["city"] = source_df["city"].values
        features_df["state"] = source_df["state"].values
        return features_df

    train_processed = build_split_df(train_df, X_train_trans)
    val_processed = build_split_df(val_df, X_val_trans)
    test_processed = build_split_df(test_df, X_test_trans)

    # 4. Serialize Processed Splits to Parquet
    print("[5/5] Exporting Parquet artifacts and preprocessor pipeline...")
    train_processed.to_parquet(PROCESSED_DIR / "train.parquet", index=False)
    val_processed.to_parquet(PROCESSED_DIR / "val.parquet", index=False)
    test_processed.to_parquet(PROCESSED_DIR / "test.parquet", index=False)

    # Save fitted ColumnTransformer
    model_artifact_path = PROCESSED_DIR / "preprocessor.joblib"
    joblib.dump(preprocessor, model_artifact_path)

    metadata = {
        "raw_samples": len(df_raw),
        "clean_samples": len(df_clean),
        "train_samples": len(train_df),
        "val_samples": len(val_df),
        "test_samples": len(test_df),
        "features_count": len(feature_names),
        "feature_names": feature_names,
        "preprocessor_path": str(model_artifact_path),
    }

    metadata_path = PROCESSED_DIR / "pipeline_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print("=" * 75)
    print("SUCCESS: Preprocessing complete. Leakage-free artifacts generated:")
    print(f"  - Clean Dataset:  {clean_csv_path}")
    print(f"  - Train Split:    {PROCESSED_DIR / 'train.parquet'} ({len(train_df)} rows)")
    print(f"  - Val Split:      {PROCESSED_DIR / 'val.parquet'} ({len(val_df)} rows)")
    print(f"  - Test Split:     {PROCESSED_DIR / 'test.parquet'} ({len(test_df)} rows)")
    print(f"  - Preprocessor:   {model_artifact_path}")
    print(f"  - Total Features: {len(feature_names)}")
    print("=" * 75)

    return metadata


if __name__ == "__main__":
    run_pipeline()
