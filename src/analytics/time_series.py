import pandas as pd
import logging


def parse_dates(df, date_col="fetched_at"):
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    valid = df[date_col].notna().sum()
    missing = df[date_col].isna().sum()
    logging.info(f"Parsed dates: {valid} valid, {missing} missing.")
    return df, valid, missing


def extract_date_components(df, date_col="fetched_at"):
    df = df.copy()
    df["year"] = df[date_col].dt.year
    df["month"] = df[date_col].dt.month
    df["weekday"] = df[date_col].dt.weekday
    df["quarter"] = df[date_col].dt.quarter
    return df


def monthly_time_series(df, date_col="fetched_at", value_col="recall_count"):
    df = df.set_index(date_col)
    monthly = df[value_col].resample("ME").sum()
    return monthly


def yearly_time_series(df, date_col="fetched_at", value_col="recall_count"):
    df = df.set_index(date_col)
    yearly = df[value_col].resample("YE").sum()
    return yearly


def rolling_averages(series, windows=[3, 6, 12]):
    result = pd.DataFrame({"value": series})
    for w in windows:
        result[f"rolling_{w}"] = series.rolling(window=w).mean()
    return result