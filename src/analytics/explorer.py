import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from utils.logger import logging

ANALYTICS_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "processed", "analytics"))

def inspect_structure(df):
    print(f"Shape       : {df.shape}")
    print(f"Columns     : {list(df.columns)}")
    print(f"Dtypes:\n{df.dtypes}")
    logging.info(f"Dataset shape: {df.shape}, columns: {len(df.columns)}")
    return df.shape

def display_info(df):
    print("\nDataFrame Info")
    df.info()
    logging.info("DataFrame info displayed")

def describe_stats(df):
    print("\nDescriptive Statistics")
    stats = df.describe(include="all")
    print(stats)
    logging.info("Descriptive statistics generated")
    return stats

def value_counts_report(df):
    print("\nValue Counts for Categorical Columns")
    results = {}
    for col in df.select_dtypes(include=["object", "category"]).columns[:5]:
        vc = df[col].value_counts().head(5)
        print(f"\n{col}:\n{vc}")
        results[col] = vc
    logging.info("Value counts report generated")
    return results

def nunique_report(df):
    print("\nUnique Value Counts")
    safe_cols = []
    for col in df.columns:
        try:
            if df[col].apply(lambda x: not isinstance(x, (list, dict))).values.all():
                safe_cols.append(col)
        except Exception:
            pass
    report = df[safe_cols].nunique().sort_values(ascending=False)
    print(report)
    logging.info("Nunique report generated")
    return report

def extract_release_years(df):
    for col in ["release_date", "fetched_at", "stored_at", "date"]:
        if col in df.columns:
            df["release_year"] = pd.to_datetime(df[col], errors="coerce").dt.year
            logging.info(f"Extracted release years from column: {col}")
            print(f"Release years extracted from '{col}'")
            return df
    logging.warning("No date column found for year extraction")
    return df

def save_chart(fig, filename):
    os.makedirs(ANALYTICS_DIR, exist_ok=True)
    path = os.path.join(ANALYTICS_DIR, filename)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    logging.info(f"Chart saved: {path}")
    return path

def plot_distributions(df):
    paths = []

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if numeric_cols:
        col = numeric_cols[0]
        fig, ax = plt.subplots()
        df[col].dropna().hist(ax=ax, bins=20)
        ax.set_title(f"Distribution of {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Count")
        paths.append(save_chart(fig, f"dist_{col}.png"))

    if "release_year" in df.columns:
        fig, ax = plt.subplots()
        df["release_year"].dropna().value_counts().sort_index().plot(kind="bar", ax=ax)
        ax.set_title("Records by Year")
        ax.set_xlabel("Year")
        ax.set_ylabel("Count")
        paths.append(save_chart(fig, "dist_release_year.png"))

    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if cat_cols:
        col = cat_cols[0]
        fig, ax = plt.subplots()
        df[col].value_counts().head(10).plot(kind="bar", ax=ax)
        ax.set_title(f"Top 10 values: {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Count")
        paths.append(save_chart(fig, f"dist_{col}.png"))

    if "_collection" in df.columns:
        fig, ax = plt.subplots()
        df["_collection"].value_counts().plot(kind="bar", ax=ax)
        ax.set_title("Records by Collection")
        ax.set_xlabel("Collection")
        ax.set_ylabel("Count")
        paths.append(save_chart(fig, "dist_collections.png"))

    logging.info(f"Saved {len(paths)} distribution charts")
    return paths

def run_exploration(df):
    logging.info("Starting EDA")
    inspect_structure(df)
    display_info(df)
    describe_stats(df)
    value_counts_report(df)
    nunique_report(df)
    df = extract_release_years(df)
    paths = plot_distributions(df)
    logging.info("EDA complete")
    return df, paths

if __name__ == "__main__":
    from src.analytics.data_loader import load_from_mongodb
    df = load_from_mongodb()
    run_exploration(df)