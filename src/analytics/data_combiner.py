import pandas as pd
import logging


def merge_dataframes(df_left, df_right, on="make", how="inner"):
    merged = pd.merge(df_left, df_right, on=on, how=how)
    logging.info(f"Merge type '{how}' resulted in {len(merged)} rows.")
    return merged


def compare_join_types(df_left, df_right, on="make"):
    results = {}
    for join_type in ["inner", "left", "right", "outer"]:
        merged = pd.merge(df_left, df_right, on=on, how=join_type)
        results[join_type] = len(merged)
        logging.info(f"Join '{join_type}': {len(merged)} rows")
    return results


def concat_dataframes(df_list):
    combined = pd.concat(df_list, ignore_index=True)
    logging.info(f"Concatenated {len(df_list)} DataFrames into {len(combined)} rows.")
    return combined