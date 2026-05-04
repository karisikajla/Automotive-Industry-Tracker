import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))

import re
import pandas as pd
from utils.logger import logging

YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")
NUMBER_PATTERN = re.compile(r"\d+\.?\d*")
ID_PATTERN = re.compile(r"^[A-Za-z0-9_\-]+$")
SHORT_TEXT_THRESHOLD = 20

def extract_years_from_titles(df):
    title_col = next((c for c in ["data.title", "data.make", "data.model", "title", "make", "model", "name"] if c in df.columns), None)
    if title_col is None:
        logging.warning("No title column found for year extraction")
        return {}
    results = {}
    for idx, val in df[title_col].dropna().items():
        found = YEAR_PATTERN.findall(str(val))
        if found:
            results[idx] = found
    logging.info(f"Extracted years from {len(results)} titles")
    print(f"Titles with years: {len(results)}")
    return results

def extract_numbers_from_titles(df):
    title_col = next((c for c in ["data.title", "data.make", "data.model", "title", "make", "model", "name"] if c in df.columns), None)
    if title_col is None:
        logging.warning("No title column found for number extraction")
        return {}
    results = {}
    for idx, val in df[title_col].dropna().items():
        found = NUMBER_PATTERN.findall(str(val))
        if found:
            results[idx] = found
    logging.info(f"Extracted numbers from {len(results)} titles")
    print(f"Titles with numbers: {len(results)}")
    return results

def filter_titles_by_prefix(df, prefix):
    title_col = next((c for c in ["data.title", "data.make", "data.model", "title", "make", "model", "name"] if c in df.columns), None)
    if title_col is None:
        logging.warning("No title column found for prefix filter")
        return df.iloc[0:0]
    pattern = re.compile(f"^{re.escape(prefix)}", re.IGNORECASE)
    mask = df[title_col].dropna().apply(lambda x: bool(pattern.match(str(x))))
    result = df.loc[mask.index[mask]]
    logging.info(f"Prefix filter '{prefix}': {len(result)} matches")
    print(f"Titles starting with '{prefix}': {len(result)}")
    return result

def count_recall_terms(df):
    text_col = next((c for c in ["data.description", "data.text", "data.raw_text", "summary", "overview", "description"] if c in df.columns), None)
    if text_col is None:
        logging.warning("No text column found for recall term counting")
        return 0
    recall_pattern = re.compile(r"\b(recall|defect|failure|crash|brake|engine|fire|safety)\b", re.IGNORECASE)
    total = df[text_col].dropna().apply(lambda x: len(recall_pattern.findall(str(x)))).sum()
    logging.info(f"Recall-related terms found: {total}")
    print(f"Recall-related terms in '{text_col}': {total}")
    return total

def identify_short_texts(df):
    text_col = next((c for c in ["data.description", "data.text", "data.raw_text", "summary", "overview", "description"] if c in df.columns), None)
    if text_col is None:
        logging.warning("No text column found for short text identification")
        return df.iloc[0:0]
    mask = df[text_col].dropna().apply(lambda x: len(str(x)) < SHORT_TEXT_THRESHOLD)
    result = df.loc[mask.index[mask]]
    logging.info(f"Short texts (< {SHORT_TEXT_THRESHOLD} chars): {len(result)}")
    print(f"Short texts found: {len(result)}")
    return result

def validate_ids(df):
    id_col = next((c for c in ["data.make", "data.model", "id", "_id", "vehicle_id", "recall_id", "source_id"] if c in df.columns), None)
    if id_col is None:
        logging.warning("No ID column found for validation")
        return {}
    valid = df[id_col].dropna().apply(lambda x: bool(ID_PATTERN.match(str(x))))
    report = {
        "total": len(valid),
        "valid": int(valid.sum()),
        "invalid": int((~valid).sum())
    }
    logging.info(f"ID validation: {report}")
    print(f"ID validation report: {report}")
    return report

def run_regex_analysis(df):
    logging.info("Starting regex analysis")
    print("\n=== Regex Operations ===")
    extract_years_from_titles(df)
    extract_numbers_from_titles(df)
    filter_titles_by_prefix(df, "A")
    count_recall_terms(df)
    identify_short_texts(df)
    validate_ids(df)
    logging.info("Regex analysis complete")

if __name__ == "__main__":
    from analytics.data_loader import load_from_mongodb
    df = load_from_mongodb()
    run_regex_analysis(df)
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')
LANG_CODE_PATTERN = re.compile(r'^[a-z]{2}$')

def detect_invalid_dates(df):
    date_col = next((c for c in ["fetched_at", "data.scraped_at", "data.processed_at"] if c in df.columns), None)
    if date_col is None:
        logging.warning("No date column found for invalid date detection")
        return {}
    invalid = df[date_col].dropna().apply(lambda x: not bool(DATE_PATTERN.match(str(x)[:10])))
    result = df.loc[invalid.index[invalid]]
    logging.info(f"Invalid dates in '{date_col}': {len(result)}")
    print(f"Invalid dates in '{date_col}': {len(result)}")
    return result

def detect_invalid_language_codes(df):
    lang_col = next((c for c in ["language", "lang", "original_language"] if c in df.columns), None)
    if lang_col is None:
        logging.warning("No language column found for validation")
        return {}
    invalid = df[lang_col].dropna().apply(lambda x: not bool(LANG_CODE_PATTERN.match(str(x))))
    result = df.loc[invalid.index[invalid]]
    logging.info(f"Invalid language codes in '{lang_col}': {len(result)}")
    print(f"Invalid language codes in '{lang_col}': {len(result)}")
    return result

def extract_numbers_from_text(df):
    text_col = next((c for c in ["data.description", "data.text", "data.raw_text"] if c in df.columns), None)
    if text_col is None:
        logging.warning("No text column found for number extraction")
        return {}
    results = {}
    for idx, val in df[text_col].dropna().items():
        found = NUMBER_PATTERN.findall(str(val))
        if found:
            results[idx] = found
    logging.info(f"Extracted numbers from text in {len(results)} rows")
    print(f"Rows with numbers in text: {len(results)}")
    return results

def flag_short_overviews(df, min_length=30):
    text_col = next((c for c in ["data.description", "data.text", "data.raw_text"] if c in df.columns), None)
    if text_col is None:
        logging.warning("No text column found for short overview flagging")
        return df.iloc[0:0]
    mask = df[text_col].dropna().apply(lambda x: len(str(x)) < min_length)
    result = df.loc[mask.index[mask]]
    logging.info(f"Short overviews (< {min_length} chars): {len(result)}")
    print(f"Short overviews found: {len(result)}")
    return result
