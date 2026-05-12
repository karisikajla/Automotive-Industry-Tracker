import pandas as pd
import logging


def top_makes_by_recalls(df, make_col="make", recall_col="total_recalls", n=5):
    top = df.nlargest(n, recall_col)[[make_col, recall_col]]
    logging.info(f"Top {n} makes by recalls computed.")
    return top


def recall_rate_by_make(df, make_col="make", recall_col="total_recalls", count_col="count"):
    df = df.copy()
    df["recall_rate"] = df[recall_col] / df[count_col]
    result = df[[make_col, "recall_rate"]].sort_values("recall_rate", ascending=False)
    logging.info("Recall rate by make computed.")
    return result


def yearly_volume(df, year_col="year_x", make_col="make"):
    volume = df.groupby([year_col, make_col]).size().reset_index(name="count")
    logging.info("Yearly volume computed.")
    return volume


def source_distribution(df, source_col="source_x"):
    dist = df[source_col].value_counts().reset_index()
    dist.columns = ["source", "count"]
    logging.info("Source distribution computed.")
    return dist


def run_all_questions(df_combined, df_mongo_agg):
    print("=" * 50)
    print("ANALYTICAL FINDINGS")
    print("=" * 50)

    print("\n1. Top makes by total recalls:")
    print(top_makes_by_recalls(df_mongo_agg))

    print("\n2. Recall rate by make:")
    print(recall_rate_by_make(df_mongo_agg))

    print("\n3. Yearly vehicle volume:")
    print(yearly_volume(df_combined))

    print("\n4. Data source distribution:")
    print(source_distribution(df_combined))