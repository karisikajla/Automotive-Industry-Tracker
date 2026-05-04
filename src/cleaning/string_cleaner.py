import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))

import pandas as pd
import re
from utils.logger import logging

def clean_title(df, col="data.make"):
    if col not in df.columns:
        logging.warning(f"Column '{col}' not found for title cleaning")
        return df
    df[col] = df[col].astype(str).str.strip().str.title()
    logging.info(f"Cleaned title column: '{col}'")
    return df

def normalize_source(df, col="source"):
    if col not in df.columns:
        logging.warning(f"Column '{col}' not found for source normalization")
        return df
    df[col] = df[col].astype(str).str.strip().str.lower()
    logging.info(f"Normalized source column: '{col}'")
    return df

def clean_text_column(df, col):
    if col not in df.columns:
        logging.warning(f"Column '{col}' not found for text cleaning")
        return df
    df[col] = df[col].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
    logging.info(f"Cleaned text column: '{col}'")
    return df

def normalize_model(df, col="data.model"):
    if col not in df.columns:
        logging.warning(f"Column '{col}' not found for model normalization")
        return df
    df[col] = df[col].astype(str).str.strip().str.upper()
    logging.info(f"Normalized model column: '{col}'")
    return df

def extract_year_column(df, date_col="fetched_at", year_col="release_year"):
    if date_col not in df.columns:
        logging.warning(f"Column '{date_col}' not found for year extraction")
        return df
    df[year_col] = pd.to_datetime(df[date_col], errors="coerce").dt.year
    logging.info(f"Extracted year from '{date_col}' into '{year_col}'")
    return df

def run_string_cleaning(df):
    logging.info("Starting string cleaning")
    df = clean_title(df)
    df = normalize_source(df)
    df = normalize_model(df)
    df = clean_text_column(df, "data.description")
    df = extract_year_column(df)
    logging.info("String cleaning complete")
    return df

if __name__ == "__main__":
    from analytics.data_loader import load_from_csv
    df = load_from_csv()
    df = run_string_cleaning(df)
    print(df[["data.make", "source", "data.model"]].head())