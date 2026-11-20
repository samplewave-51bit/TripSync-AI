"""
TripSync AI - Exploratory Data Analysis (EDA) Pipeline
Performs in-depth statistical profiling, correlation analysis, and exports publication-grade visualizations.
Output Directory: ml_pipeline/reports/figures/
"""

import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless execution
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_FILE = ROOT_DIR / "data" / "processed" / "places_cleaned.csv"
REPORTS_DIR = ROOT_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# Configure visual styling
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8


def load_dataset() -> pd.DataFrame:
    """Loads clean processed reference dataset."""
    if not PROCESSED_FILE.exists():
        raise FileNotFoundError(f"Clean data not found at {PROCESSED_FILE}. Run preprocessing.py first.")
    return pd.read_csv(PROCESSED_FILE)


def plot_target_distribution(df: pd.DataFrame):
    """1. Target Variable (Rating) Distribution with KDE."""
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(df["rating"], kde=True, bins=15, color="#2b5c8f", edgecolor="black", alpha=0.7, ax=ax)
    mean_val = df["rating"].mean()
    median_val = df["rating"].median()
    ax.axvline(mean_val, color="#e63946", linestyle="--", linewidth=2, label=f"Mean: {mean_val:.2f}")
    ax.axvline(median_val, color="#2a9d8f", linestyle="-", linewidth=2, label=f"Median: {median_val:.2f}")
    ax.set_title("Distribution of Google Review Ratings (Target Variable)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Review Rating (Scale: 1.0 - 5.0)", fontsize=11)
    ax.set_ylabel("Attraction Count", fontsize=11)
    ax.legend(frameon=True, facecolor="white", loc="upper left")
    plt.tight_layout()
    output_path = FIGURES_DIR / "01_target_rating_distribution.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"  [SAVED] {output_path.name}")


def plot_macro_categories(df: pd.DataFrame):
    """2. Macro-Thematic Experience Categories."""
    fig, ax = plt.subplots(figsize=(9, 5))
    counts = df["macro_category"].value_counts()
    colors = ["#264653", "#2a9d8f", "#e76f51", "#f4a261", "#457b9d"]
    bars = ax.bar(counts.index.str.replace("_", " ").str.title(), counts.values, color=colors, edgecolor="black", alpha=0.85)
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h} ({h/len(df)*100:.1f}%)", xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_title("Attraction Distribution Across 5 Macro-Thematic Dimensions", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Experience Dimension", fontsize=11)
    ax.set_ylabel("Attraction Count", fontsize=11)
    ax.set_ylim(0, max(counts.values) * 1.15)
    plt.tight_layout()
    output_path = FIGURES_DIR / "02_macro_thematic_distribution.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"  [SAVED] {output_path.name}")


def plot_zonal_and_state_coverage(df: pd.DataFrame):
    """3. Pan-India Zonal and State Coverage."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Zone
    zone_counts = df["zone"].value_counts()
    ax1.pie(zone_counts.values, labels=zone_counts.index, autopct="%1.1f%%", startangle=140,
            colors=sns.color_palette("Set2", len(zone_counts)), wedgeprops={"edgecolor": "black", "linewidth": 0.8})
    ax1.set_title("Pan-India Zonal Breakdown", fontsize=13, fontweight="bold")

    # Top 10 States
    top_states = df["state"].value_counts().head(10)
    sns.barplot(x=top_states.values, y=top_states.index, palette="viridis", edgecolor="black", ax=ax2)
    ax2.set_title("Top 10 Indian States by Attraction Count", fontsize=13, fontweight="bold")
    ax2.set_xlabel("Number of Attractions", fontsize=11)
    ax2.set_ylabel("State", fontsize=11)

    plt.tight_layout()
    output_path = FIGURES_DIR / "03_zonal_and_state_coverage.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"  [SAVED] {output_path.name}")


def plot_budget_and_fees(df: pd.DataFrame):
    """4. Budget Tier and Entrance Fee Distributions."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Budget Tiers
    budget_counts = df["budget_tier"].value_counts()
    ax1.bar(budget_counts.index, budget_counts.values, color=["#2a9d8f", "#e9c46a", "#e76f51"], edgecolor="black")
    for idx, val in enumerate(budget_counts.values):
        ax1.text(idx, val + 5, f"{val} ({val/len(df)*100:.1f}%)", ha="center", fontweight="bold")
    ax1.set_title("Attraction Distribution by Budget Tier", fontsize=13, fontweight="bold")
    ax1.set_ylabel("Count", fontsize=11)
    ax1.set_ylim(0, max(budget_counts.values) * 1.15)

    # Log Entrance Fee Boxplot across Budget Tiers
    sns.boxplot(x="budget_tier", y="log_entrance_fee", data=df, palette="Pastel1", ax=ax2)
    ax2.set_title("Log(1 + Entrance Fee in INR) by Budget Tier", fontsize=13, fontweight="bold")
    ax2.set_xlabel("Budget Tier", fontsize=11)
    ax2.set_ylabel("Log(1 + Fee)", fontsize=11)

    plt.tight_layout()
    output_path = FIGURES_DIR / "04_budget_tier_and_fees.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"  [SAVED] {output_path.name}")


def plot_duration_by_category(df: pd.DataFrame):
    """5. Visit Duration Distribution by Macro-Category."""
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(x="macro_category", y="time_needed_hrs", data=df, palette="Accent", ax=ax)
    sns.stripplot(x="macro_category", y="time_needed_hrs", data=df, color="black", alpha=0.3, jitter=0.2, ax=ax)
    ax.set_title("Exploration Duration (Hours) by Macro-Thematic Category", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Category", fontsize=11)
    ax.set_ylabel("Time Needed to Visit (Hours)", fontsize=11)
    labels = [l.get_text().replace("_", "\n").title() for l in ax.get_xticklabels()]
    ax.set_xticklabels(labels)
    plt.tight_layout()
    output_path = FIGURES_DIR / "05_visit_duration_by_category.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"  [SAVED] {output_path.name}")


def plot_correlation_heatmap(df: pd.DataFrame):
    """6. Correlation Heatmap across Engineered Features."""
    fig, ax = plt.subplots(figsize=(10, 8))
    corr_cols = [
        "rating", "time_needed_hrs", "log_entrance_fee", "log_reviews",
        "budget_tier_code", "has_airport_50km", "is_dslr_allowed",
        "theme_culture_heritage", "theme_nature_wildlife",
        "theme_spiritual_religious", "theme_adventure_outdoor",
        "theme_urban_entertainment"
    ]
    corr_matrix = df[corr_cols].corr()
    clean_labels = [c.replace("theme_", "").replace("_", " ").title() for c in corr_cols]
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", cbar=True,
                xticklabels=clean_labels, yticklabels=clean_labels, ax=ax, linewidths=0.5)
    ax.set_title("Pearson Correlation Matrix Across Model Features", fontsize=14, fontweight="bold", pad=12)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.yticks(fontsize=9)
    plt.tight_layout()
    output_path = FIGURES_DIR / "06_feature_correlation_heatmap.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"  [SAVED] {output_path.name}")


def plot_geospatial_scatter(df: pd.DataFrame):
    """7. Pan-India Geographic Scatter Map."""
    fig, ax = plt.subplots(figsize=(9, 8))
    sns.scatterplot(
        x="longitude", y="latitude", hue="macro_category",
        data=df, palette="tab10", s=70, alpha=0.8, edgecolor="black", ax=ax
    )
    ax.set_title("Geospatial Map of 323 Indian Attractions by Macro-Theme", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Longitude (°E)", fontsize=11)
    ax.set_ylabel("Latitude (°N)", fontsize=11)
    ax.legend(title="Macro Category", frameon=True, facecolor="white", loc="upper left",
              bbox_to_anchor=(1.02, 1))
    plt.tight_layout()
    output_path = FIGURES_DIR / "07_geospatial_attraction_scatter.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"  [SAVED] {output_path.name}")


def compute_statistical_summary(df: pd.DataFrame) -> dict:
    """Computes comprehensive statistical metrics for summary export."""
    summary = {
        "total_attractions": int(len(df)),
        "states_count": int(df["state"].nunique()),
        "cities_count": int(df["city"].nunique()),
        "rating_stats": {
            "mean": float(df["rating"].mean()),
            "std": float(df["rating"].std()),
            "median": float(df["rating"].median()),
            "min": float(df["rating"].min()),
            "max": float(df["rating"].max()),
            "skewness": float(df["rating"].skew()),
        },
        "time_needed_stats": {
            "mean": float(df["time_needed_hrs"].mean()),
            "std": float(df["time_needed_hrs"].std()),
            "median": float(df["time_needed_hrs"].median()),
            "min": float(df["time_needed_hrs"].min()),
            "max": float(df["time_needed_hrs"].max()),
        },
        "fee_stats_inr": {
            "mean": float(df["entrance_fee_inr"].mean()),
            "median": float(df["entrance_fee_inr"].median()),
            "min": float(df["entrance_fee_inr"].min()),
            "max": float(df["entrance_fee_inr"].max()),
            "zero_fee_pct": float((df["entrance_fee_inr"] == 0).mean() * 100),
        },
        "reviews_lakhs_stats": {
            "mean": float(df["reviews_lakhs"].mean()),
            "median": float(df["reviews_lakhs"].median()),
            "max": float(df["reviews_lakhs"].max()),
        },
        "macro_category_counts": df["macro_category"].value_counts().to_dict(),
        "zonal_counts": df["zone"].value_counts().to_dict(),
        "budget_tier_counts": df["budget_tier"].value_counts().to_dict(),
    }
    return summary


def run_eda():
    """Main execution entrypoint for EDA generation."""
    print("=" * 75)
    print("TRIPSYNC AI: COMPREHENSIVE EXPLORATORY DATA ANALYSIS (EDA)")
    print("=" * 75)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    df = load_dataset()
    print(f"Loaded clean dataset with {len(df)} attractions.")

    print("\n[Generating Publication-Grade Visualizations]:")
    plot_target_distribution(df)
    plot_macro_categories(df)
    plot_zonal_and_state_coverage(df)
    plot_budget_and_fees(df)
    plot_duration_by_category(df)
    plot_correlation_heatmap(df)
    plot_geospatial_scatter(df)

    print("\n[Computing Descriptive Statistical Profiles]:")
    summary = compute_statistical_summary(df)
    summary_path = REPORTS_DIR / "eda_summary_statistics.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  [SAVED] {summary_path.name}")

    print("\n" + "=" * 75)
    print("EDA Successfully Completed. All figures and summaries exported.")
    print("=" * 75)


if __name__ == "__main__":
    run_eda()
