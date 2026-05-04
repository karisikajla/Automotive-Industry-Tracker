import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))

import pandas as pd
from utils.logger import logging

def convert_dates(df, date_cols):
    for col in date_cols:
        if col not in df.columns:
            logging.warning(f"Date column '{col}' not found")
            continue
        df[col] = pd.to_datetime(df[col], errors="coerce")
        logging.info(f"Converted '{col}' to datetime")
    return df

def convert_numeric(df, float_cols=None, int_cols=None):
    if float_cols:
        for col in float_cols:
            if col not in df.columns:
                continue
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("float32")
            logging.info(f"Converted '{col}' to float32")
    if int_cols:
        for col in int_cols:
            if col not in df.columns:
                continue
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
            logging.info(f"Converted '{col}' to Int64")
    return df

def convert_categorical(df, cat_cols):
    for col in cat_cols:
        if col not in df.columns:
            logging.warning(f"Category column '{col}' not found")
            continue
        df[col] = df[col].astype("category")
        logging.info(f"Converted '{col}' to category")
    return df

def memory_report(df_before, df_after):
    before_mb = df_before.memory_usage(deep=True).sum() / 1024 ** 2
    after_mb = df_after.memory_usage(deep=True).sum() / 1024 ** 2
    reduction = before_mb - after_mb
    print(f"Memory before : {before_mb:.2f} MB")
    print(f"Memory after  : {after_mb:.2f} MB")
    print(f"Reduction     : {reduction:.2f} MB")
    logging.info(f"Memory report - before: {before_mb:.2f} MB, after: {after_mb:.2f} MB, reduction: {reduction:.2f} MB")

def run_type_conversion(df):
    logging.info("Starting type conversion")
    df_before = df.copy()

    df = convert_dates(df, ["fetched_at", "data.scraped_at", "data.processed_at", "stored_at"])
    df = convert_numeric(df, float_cols=["version", "data.file_size_kb", "data.width", "data.height"])
    df = convert_categorical(df, ["source", "_collection", "data.make", "data.model", "data.type"])

    memory_report(df_before, df)
    logging.info("Type conversion complete")
    return df

if __name__ == "__main__":
    from analytics.data_loader import load_from_csv
    df = load_from_csv()
    df_before = df.copy()
    df = run_type_conversion(df)
    print(df.dtypes)