import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))

import pandas as pd
from utils.logger import logging

def select_columns(df, columns):
    available = [c for c in columns if c in df.columns]
    result = df[available]
    logging.info(f"Selected columns: {available}")
    return result

def filter_by_label(df, column, value):
    if column not in df.columns:
        logging.warning(f"Column not found for loc filter: {column}")
        return df.iloc[0:0]
    result = df.loc[df[column] == value]
    logging.info(f"loc filter on {column}=={value}: {len(result)} rows")
    return result

def sample_rows_iloc(df, start=0, end=10):
    result = df.iloc[start:end]
    logging.info(f"iloc sample rows {start}:{end}: {len(result)} rows")
    return result

def boolean_filter(df, min_count=1):
    result = df.copy()
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if numeric_cols:
        col = numeric_cols[0]
        result = result[result[col] >= min_count]
        logging.info(f"Boolean filter on {col} >= {min_count}: {len(result)} rows")
    else:
        logging.warning("No numeric columns for boolean filter")
    return result

def filter_isin(df, column, values, exclude=False):
    if column not in df.columns:
        logging.warning(f"Column not found for isin filter: {column}")
        return df.iloc[0:0]
    mask = df[column].isin(values)
    if exclude:
        mask = ~mask
    result = df[mask]
    logging.info(f"isin filter on {column} (exclude={exclude}): {len(result)} rows")
    return result

def filter_between(df, column, low, high):
    if column not in df.columns:
        logging.warning(f"Column not found for between filter: {column}")
        return df.iloc[0:0]
    result = df[df[column].between(low, high)]
    logging.info(f"between filter on {column} [{low}, {high}]: {len(result)} rows")
    return result

def run_selection_demo(df):
    logging.info("Starting selection demo")
    print("\nColumn Selection")
    cols = df.columns[:3].tolist()
    subset = select_columns(df, cols)
    print(subset.head(3))

    print("\niloc Sample")
    sample = sample_rows_iloc(df, 0, 5)
    print(sample)

    print("\nBoolean Filter")
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if numeric_cols:
        filtered = boolean_filter(df, min_count=1)
        print(f"Rows after boolean filter: {len(filtered)}")

    print("\nisin Filter")
    if "_collection" in df.columns:
        collections = df["_collection"].dropna().unique()[:2].tolist()
        isin_result = filter_isin(df, "_collection", collections)
        print(f"isin result: {len(isin_result)} rows")
        excluded = filter_isin(df, "_collection", collections, exclude=True)
        print(f"isin exclude result: {len(excluded)} rows")

    print("\nbetween Filter")
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if numeric_cols:
        col = numeric_cols[0]
        low = float(df[col].quantile(0.25))
        high = float(df[col].quantile(0.75))
        between_result = filter_between(df, col, low, high)
        print(f"between filter on {col} [{low:.2f}, {high:.2f}]: {len(between_result)} rows")

    logging.info("Selection demo complete")

if __name__ == "__main__":
    from analytics.data_loader import load_from_mongodb
    df = load_from_mongodb()
    run_selection_demo(df)