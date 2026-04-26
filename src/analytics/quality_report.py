import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from utils.logger import logging

ANALYTICS_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "processed", "analytics"))

def missing_value_report(df):
    total = len(df)
    missing = df.isnull().sum()
    pct = (missing / total * 100).round(2)
    report = pd.DataFrame({
        "missing_count": missing,
        "missing_pct": pct,
        "severity": pd.cut(pct, bins=[-1, 0, 10, 50, 100], labels=["none", "low", "medium", "high"])
    })
    report = report[report["missing_count"] > 0].sort_values("missing_pct", ascending=False)
    logging.info(f"Missing value report: {len(report)} columns with missing values")
    print("\nMissing Value Report")
    print(report)
    return report

def detect_zero_values(df):
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    results = {}
    for col in numeric_cols:
        try:
            zero_count = int((df[col] == 0).sum())
            if zero_count > 0:
                results[col] = zero_count
        except Exception:
            pass
    if not results:
        logging.info("No zero values found in numeric columns")
        print("\nZero Value Detection\nNo zero values found")
        return pd.DataFrame(columns=["zero_count", "zero_pct"])
    report = pd.DataFrame.from_dict(results, orient="index", columns=["zero_count"])
    report["zero_count"] = report["zero_count"].astype(int)
    report["zero_pct"] = (report["zero_count"] / len(df) * 100).round(2)
    logging.info(f"Zero value detection: {len(results)} columns with zeros")
    print("\nZero Value Detection")
    print(report)
    return report

def detect_outliers_iqr(df):
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    results = {}
    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outliers = df[(df[col] < lower) | (df[col] > upper)]
        if len(outliers) > 0:
            results[col] = {
                "outlier_count": len(outliers),
                "lower_bound": round(lower, 4),
                "upper_bound": round(upper, 4)
            }
    report = pd.DataFrame(results).T
    logging.info(f"IQR outlier detection: {len(results)} columns with outliers")
    print("\nIQR Outlier Detection")
    print(report)
    return report

def detect_duplicate_ids(df):
    id_col = next((c for c in ["id", "_id", "vehicle_id", "recall_id"] if c in df.columns), None)
    if id_col is None:
        logging.warning("No ID column found for duplicate detection")
        return 0
    duplicates = df[id_col].duplicated().sum()
    logging.info(f"Duplicate IDs found: {duplicates}")
    print(f"\nDuplicate IDs in '{id_col}': {duplicates}")
    return duplicates

def detect_invalid_titles(df):
    title_col = next((c for c in ["title", "make", "model", "name"] if c in df.columns), None)
    if title_col is None:
        logging.warning("No title column found")
        return 0
    empty = df[title_col].isnull().sum()
    blank = (df[title_col].astype(str).str.strip() == "").sum()
    total_invalid = empty + blank
    logging.info(f"Invalid titles: {total_invalid} (empty: {empty}, blank: {blank})")
    print(f"\nInvalid titles: {total_invalid} (empty: {empty}, blank: {blank})")
    return total_invalid

def plot_missing_heatmap(df):
    os.makedirs(ANALYTICS_DIR, exist_ok=True)
    cols_with_missing = df.columns[df.isnull().any()].tolist()
    if not cols_with_missing:
        logging.info("No missing values to plot in heatmap")
        print("No missing values found — heatmap skipped")
        return None
    sample = df[cols_with_missing].head(50)
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(sample.isnull(), cbar=False, yticklabels=False, ax=ax)
    ax.set_title("Missing Value Heatmap (first 50 rows)")
    path = os.path.join(ANALYTICS_DIR, "missing_heatmap.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    logging.info(f"Missing value heatmap saved: {path}")
    print(f"Heatmap saved: {path}")
    return path

def full_quality_audit(df):
    logging.info("Starting full quality audit")
    issues = []

    missing = missing_value_report(df)
    for col, row in missing.iterrows():
        issues.append({
            "column": col,
            "issue_type": "missing_values",
            "count": row["missing_count"],
            "pct": row["missing_pct"],
            "severity": str(row["severity"])
        })

    zeros = detect_zero_values(df)
    for col, row in zeros.iterrows():
        issues.append({
            "column": col,
            "issue_type": "zero_values",
            "count": row["zero_count"],
            "pct": row["zero_pct"],
            "severity": "medium" if row["zero_pct"] > 10 else "low"
        })

    outliers = detect_outliers_iqr(df)
    for col, row in outliers.iterrows():
        issues.append({
            "column": col,
            "issue_type": "outliers",
            "count": int(row["outlier_count"]),
            "pct": round(int(row["outlier_count"]) / len(df) * 100, 2),
            "severity": "medium"
        })

    dup_count = detect_duplicate_ids(df)
    if dup_count > 0:
        issues.append({
            "column": "id",
            "issue_type": "duplicate_ids",
            "count": dup_count,
            "pct": round(dup_count / len(df) * 100, 2),
            "severity": "high"
        })

    invalid_titles = detect_invalid_titles(df)
    if invalid_titles > 0:
        issues.append({
            "column": "title",
            "issue_type": "invalid_titles",
            "count": invalid_titles,
            "pct": round(invalid_titles / len(df) * 100, 2),
            "severity": "high"
        })

    report_df = pd.DataFrame(issues)
    os.makedirs(ANALYTICS_DIR, exist_ok=True)
    path = os.path.join(ANALYTICS_DIR, "quality_report.csv")
    report_df.to_csv(path, index=False)
    logging.info(f"Quality report saved: {path}, total issues: {len(issues)}")
    print(f"\nQuality report saved: {path}")
    print(f"Total issues found: {len(issues)}")
    return report_df

if __name__ == "__main__":
    from analytics.data_loader import load_from_mongodb
    df = load_from_mongodb()
    full_quality_audit(df)
    plot_missing_heatmap(df)