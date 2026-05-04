import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))

import pandas as pd
from utils.logger import logging

def validate_no_null_critical(df, critical_cols):
    for col in critical_cols:
        if col not in df.columns:
            logging.warning(f"Column '{col}' not found for validation")
            continue
        null_count = df[col].isnull().sum()
        assert null_count == 0, f"Validation failed: '{col}' has {null_count} null values"
        logging.info(f"Validation passed: '{col}' has no null values")
    print("Validation passed: no null values in critical columns")

def validate_year_range(df, year_col="release_year", min_year=1900, max_year=2030):
    if year_col not in df.columns:
        logging.warning(f"Column '{year_col}' not found for year validation")
        return
    valid = df[year_col].dropna()
    invalid = valid[(valid < min_year) | (valid > max_year)]
    assert len(invalid) == 0, f"Validation failed: {len(invalid)} invalid years in '{year_col}'"
    logging.info(f"Validation passed: all years in '{year_col}' are within [{min_year}, {max_year}]")
    print(f"Validation passed: year range [{min_year}, {max_year}]")

def validate_no_duplicates(df, col):
    if col not in df.columns:
        logging.warning(f"Column '{col}' not found for duplicate validation")
        return
    dup_count = df[col].duplicated().sum()
    assert dup_count == 0, f"Validation failed: '{col}' has {dup_count} duplicate values"
    logging.info(f"Validation passed: '{col}' has no duplicates")
    print(f"Validation passed: no duplicates in '{col}'")

def validate_column_types(df, expected_types):
    for col, expected in expected_types.items():
        if col not in df.columns:
            logging.warning(f"Column '{col}' not found for type validation")
            continue
        actual = str(df[col].dtype)
        assert expected in actual, f"Validation failed: '{col}' expected {expected}, got {actual}"
        logging.info(f"Validation passed: '{col}' dtype is {actual}")
    print("Validation passed: all column types correct")

def run_validation(df):
    logging.info("Starting validation")
    try:
        validate_no_null_critical(df, ["source", "_collection"])
        validate_year_range(df)
        validate_column_types(df, {
            "fetched_at": "datetime",
            "version": "float"
        })
        logging.info("All validations passed")
        print("All validations passed")
    except AssertionError as e:
        logging.error(f"Validation error: {e}")
        print(f"Validation error: {e}")

if __name__ == "__main__":
    from analytics.data_loader import load_from_csv
    df = load_from_csv()
    run_validation(df)