import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))

import pandas as pd
from utils.logger import logging
from cleaning.missing_handler import drop_missing_critical, fill_text_fields, replace_zero_with_nan, fill_numeric_with_median, drop_high_missing_columns
from cleaning.string_cleaner import run_string_cleaning
from cleaning.deduplicator import run_deduplication
from cleaning.type_converter import run_type_conversion
from cleaning.validator import run_validation

CLEANED_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "processed", "cleaned"))

def run_cleaning_pipeline(df):
    logging.info("Starting cleaning pipeline")
    df = df.copy()

    logging.info("Step 1: Dropping high missing columns")
    df = drop_high_missing_columns(df, threshold=0.9)

    logging.info("Step 2: Dropping rows with missing critical columns")
    df = drop_missing_critical(df, critical_cols=["source", "_collection"])

    logging.info("Step 3: Filling text fields")
    df = fill_text_fields(df, text_cols=["data.make", "data.model", "data.description", "data.type"])

    logging.info("Step 4: Replacing zeros with NaN")
    df = replace_zero_with_nan(df, numeric_cols=["data.width", "data.height", "data.file_size_kb"])

    logging.info("Step 5: Filling numeric with median")
    df = fill_numeric_with_median(df)

    logging.info("Step 6: String cleaning")
    df = run_string_cleaning(df)

    logging.info("Step 7: Deduplication")
    df = run_deduplication(df)

    logging.info("Step 8: Type conversion")
    df = run_type_conversion(df)

    logging.info("Step 9: Validation")
    run_validation(df)

    os.makedirs(CLEANED_DIR, exist_ok=True)
    output_path = os.path.join(CLEANED_DIR, "cleaned_data.csv")
    df.to_csv(output_path, index=False)
    logging.info(f"Cleaned dataset saved: {output_path}, shape: {df.shape}")
    print(f"Cleaned dataset saved: {output_path}")
    print(f"Final shape: {df.shape}")

    return df

if __name__ == "__main__":
    from analytics.data_loader import load_from_csv
    df = load_from_csv()
    df_clean = run_cleaning_pipeline(df)