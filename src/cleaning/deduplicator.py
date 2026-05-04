import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))

import pandas as pd
from utils.logger import logging

def count_duplicates(df, col=None):
    if col is None:
        count = df.duplicated().sum()
        logging.info(f"Exact duplicate rows: {count}")
        print(f"Exact duplicate rows: {count}")
    else:
        if col not in df.columns:
            logging.warning(f"Column '{col}' not found")
            return 0
        count = df[col].duplicated().sum()
        logging.info(f"Duplicate values in '{col}': {count}")
        print(f"Duplicate values in '{col}': {count}")
    return count

def drop_exact_duplicates(df):
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    logging.info(f"Dropped {before - after} exact duplicate rows")
    print(f"Rows before: {before}, after dropping exact duplicates: {after}")
    return df

def drop_duplicate_ids(df, id_col):
    if id_col not in df.columns:
        logging.warning(f"ID column '{id_col}' not found")
        return df
    before = len(df)
    df = df.drop_duplicates(subset=[id_col], keep="first")
    after = len(df)
    logging.info(f"Dropped {before - after} rows with duplicate '{id_col}'")
    print(f"Rows after dropping duplicate '{id_col}': {after}")
    return df

def drop_duplicate_title_date(df, title_col, date_col):
    if title_col not in df.columns or date_col not in df.columns:
        logging.warning(f"Columns '{title_col}' or '{date_col}' not found")
        return df
    before = len(df)
    df = df.drop_duplicates(subset=[title_col, date_col], keep="first")
    after = len(df)
    logging.info(f"Dropped {before - after} rows with duplicate title+date")
    print(f"Rows after dropping duplicate title+date: {after}")
    return df

def run_deduplication(df):
    logging.info("Starting deduplication")
    print(f"Rows before deduplication: {len(df)}")
    count_duplicates(df)
    df = drop_exact_duplicates(df)
    count_duplicates(df, col="source")
    df = drop_duplicate_ids(df, id_col="source")
    df = drop_duplicate_title_date(df, title_col="data.make", date_col="fetched_at")
    logging.info("Deduplication complete")
    return df

if __name__ == "__main__":
    from analytics.data_loader import load_from_csv
    df = load_from_csv()
    df = run_deduplication(df)