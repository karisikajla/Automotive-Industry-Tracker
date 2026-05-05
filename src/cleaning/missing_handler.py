import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))

import pandas as pd
import numpy as np
from utils.logger import logging

CLEANED_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "processed", "cleaned"))

def report_missing(df):
    total = len(df)
    missing = df.isnull().sum()
    pct = (missing / total * 100).round(2)
    report = pd.DataFrame({
        "missing_count": missing,
        "missing_pct": pct
    })
    report = report[report["missing_count"] > 0].sort_values("missing_pct", ascending=False)
    logging.info(f"Missing value report: {len(report)} columns with missing values")
    print(report)
    return report

def drop_missing_critical(df, critical_cols):
    before = len(df)
    existing = [c for c in critical_cols if c in df.columns]
    df = df.dropna(subset=existing)
    after = len(df)
    logging.info(f"Dropped {before - after} rows with missing critical columns: {existing}")
    print(f"Dropped {before - after} rows missing critical columns")
    return df

def fill_text_fields(df, text_cols, placeholder="unknown"):
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna(placeholder)
            logging.info(f"Filled missing text in '{col}' with '{placeholder}'")
    return df

def replace_zero_with_nan(df, numeric_cols):
    for col in numeric_cols:
        if col in df.columns:
            count = (df[col] == 0).sum()
            df[col] = df[col].replace(0, np.nan)
            logging.info(f"Replaced {count} zeros with NaN in '{col}'")
    return df

def fill_numeric_with_median(df):
    numeric_cols = df.select_dtypes(include=["number"]).columns
    for col in numeric_cols:
        median = df[col].median()
        missing = df[col].isnull().sum()
        if missing > 0:
            df[col] = df[col].fillna(median)
            logging.info(f"Filled {missing} missing values in '{col}' with median {median:.4f}")
    return df

def drop_high_missing_columns(df, threshold=0.9):
    total = len(df)
    to_drop = [col for col in df.columns if df[col].isnull().sum() / total > threshold]
    df = df.drop(columns=to_drop)
    logging.info(f"Dropped {len(to_drop)} columns with >{threshold*100}% missing: {to_drop}")
    print(f"Dropped columns: {to_drop}")
    return df

def save_missing_report(df):
    os.makedirs(CLEANED_DIR, exist_ok=True)
    report = report_missing(df)
    path = os.path.join(CLEANED_DIR, "missing_report.csv")
    report.to_csv(path)
    logging.info(f"Missing report saved: {path}")
    return path

if __name__ == "__main__":
    from analytics.data_loader import load_from_csv
    df = load_from_csv()
    save_missing_report(df)