import pandas as pd
import logging


def genre_summary(df, group_col="make", value_col="recall_count"):
    summary = df.groupby(group_col).agg(
        mean_recalls=(value_col, "mean"),
        sum_recalls=(value_col, "sum"),
        count=(value_col, "count"),
        median_recalls=(value_col, "median")
    ).reset_index()
    logging.info(f"Genre summary created with {len(summary)} groups.")
    return summary


def yearly_trends(df, year_col="year_x", value_col="recall_count"):
    trends = df.groupby(year_col).agg(
        total_recalls=(value_col, "sum"),
        avg_recalls=(value_col, "mean"),
        count=(value_col, "count")
    ).reset_index()
    logging.info(f"Yearly trends created with {len(trends)} rows.")
    return trends


def top_n_per_group(df, group_col="make", value_col="recall_count", n=3):
    def top_n(group):
        return group.nlargest(n, value_col)
    result = df.groupby(group_col, group_keys=False).apply(top_n)
    logging.info(f"Top {n} per group computed.")
    return result