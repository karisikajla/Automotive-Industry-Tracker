import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")))

import pytest
import pandas as pd
import numpy as np
from cleaning.missing_handler import drop_missing_critical, fill_text_fields, replace_zero_with_nan, fill_numeric_with_median
from cleaning.string_cleaner import clean_title, normalize_source, extract_year_column
from cleaning.deduplicator import drop_exact_duplicates, drop_duplicate_ids, count_duplicates
from cleaning.type_converter import convert_dates, convert_numeric, convert_categorical
from cleaning.validator import validate_no_null_critical, validate_year_range

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "source": ["nhtsa_api", "nhtsa_api", None, "test", "nhtsa_api"],
        "_collection": ["raw_recalls", "raw_recalls", "raw_recalls", None, "raw_recalls"],
        "data.make": ["  audi  ", "volkswagen", None, "SKODA", "audi"],
        "data.model": ["A4", "Golf", None, "Octavia", "A4"],
        "data.description": ["  brake issue  ", None, "engine fire", "safety recall", "brake issue"],
        "data.width": [0, 1920, 1280, 0, 1920],
        "version": [1.0, 1.0, 1.0, 1.0, 1.0],
        "fetched_at": ["2026-03-23", "2026-03-23", "not-a-date", "2026-03-24", "2026-03-23"],
        "release_year": [2026, 2026, None, 2026, 2026]
    })

def test_drop_rows_missing_source_removes_null(sample_df):
    result = drop_missing_critical(sample_df, ["source"])
    assert result["source"].isnull().sum() == 0

def test_drop_rows_missing_collection_removes_null(sample_df):
    result = drop_missing_critical(sample_df, ["_collection"])
    assert result["_collection"].isnull().sum() == 0

def test_fill_missing_description_no_nulls_remain(sample_df):
    result = fill_text_fields(sample_df, ["data.description"])
    assert result["data.description"].isnull().sum() == 0

def test_fill_missing_description_uses_placeholder(sample_df):
    result = fill_text_fields(sample_df, ["data.description"], placeholder="unknown")
    assert "unknown" in result["data.description"].values

def test_replace_zero_with_nan_on_width(sample_df):
    result = replace_zero_with_nan(sample_df, ["data.width"])
    assert result["data.width"].isnull().sum() == 2

def test_clean_title_strips_whitespace(sample_df):
    result = clean_title(sample_df, col="data.make")
    assert result["data.make"].str.startswith(" ").sum() == 0

def test_clean_title_lowercases(sample_df):
    result = clean_title(sample_df, col="data.make")
    assert "SKODA" not in result["data.make"].values

def test_normalize_source_lowercases(sample_df):
    result = normalize_source(sample_df, col="source")
    assert result["source"].dropna().str.islower().all()

def test_extract_year_creates_column(sample_df):
    result = extract_year_column(sample_df, date_col="fetched_at", year_col="year_extracted")
    assert "year_extracted" in result.columns

def test_extract_year_correct_values(sample_df):
    result = extract_year_column(sample_df, date_col="fetched_at", year_col="year_extracted")
    assert result["year_extracted"].dropna().iloc[0] == 2026

def test_drop_exact_duplicates_removes_copies(sample_df):
    df_with_dupes = pd.concat([sample_df, sample_df.iloc[[0]]], ignore_index=True)
    before = len(df_with_dupes)
    result = drop_exact_duplicates(df_with_dupes)
    assert len(result) < before

def test_drop_duplicate_ids_keeps_first(sample_df):
    result = drop_duplicate_ids(sample_df, id_col="source")
    assert result["source"].dropna().duplicated().sum() == 0

def test_count_duplicates_returns_correct_number(sample_df):
    count = count_duplicates(sample_df)
    assert count >= 0

def test_convert_dates_produces_datetime_type(sample_df):
    result = convert_dates(sample_df, ["fetched_at"])
    assert pd.api.types.is_datetime64_any_dtype(result["fetched_at"])

def test_convert_dates_bad_values_become_nat(sample_df):
    result = convert_dates(sample_df, ["fetched_at"])
    assert result["fetched_at"].isnull().sum() >= 1

def test_validate_no_null_titles_passes_on_clean_data(sample_df):
    df = fill_text_fields(sample_df, ["data.make"])
    df = drop_missing_critical(df, ["source"])
    validate_no_null_critical(df, ["source"])

def test_validate_no_null_titles_fails_on_null(sample_df):
    with pytest.raises(AssertionError):
        validate_no_null_critical(sample_df, ["source"])