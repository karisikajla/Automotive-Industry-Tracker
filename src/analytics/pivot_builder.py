import pandas as pd
import logging


def wide_to_long(df, id_vars, value_vars):
    long_df = pd.melt(df, id_vars=id_vars, value_vars=value_vars, var_name="metric", value_name="value")
    logging.info(f"Converted to long format: {len(long_df)} rows.")
    return long_df


def long_to_wide(df, index, columns, values):
    wide_df = df.pivot(index=index, columns=columns, values=values)
    logging.info(f"Converted to wide format.")
    return wide_df


def build_pivot_table(df, index, columns, values, aggfunc="mean", margins=True):
    pivot = pd.pivot_table(df, index=index, columns=columns, values=values, aggfunc=aggfunc, margins=margins)
    logging.info(f"Pivot table created with shape {pivot.shape}.")
    return pivot


def build_crosstab(df, index_col, columns_col):
    ct = pd.crosstab(df[index_col], df[columns_col])
    logging.info(f"Crosstab created with shape {ct.shape}.")
    return ct