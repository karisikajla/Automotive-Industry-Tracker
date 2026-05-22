import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))

from utils.logger import logging
from visualization.static_charts import (
    plot_top_makes_by_recall_count,
    plot_recalls_over_years,
    plot_recall_distribution_by_component,
    plot_rating_boxplot_by_make,
    plot_recall_heatmap,
    plot_consequence_distribution,
    plot_cumulative_recalls_over_time,
    plot_dashboard_subplots,
)
from visualization.interactive_charts import (
    interactive_recalls_by_make,
    interactive_recalls_timeline,
    interactive_component_treemap,
    interactive_scatter_year_vs_count,
    interactive_multi_layout,
)

STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "outputs", "visualizations", "static"))
INTERACTIVE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "outputs", "visualizations", "interactive"))
DEFAULT_CSV = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "processed", "cleaned", "cleaned_data.csv"))

STATIC_CHARTS = [
    ("Top Makes by Recall Count", plot_top_makes_by_recall_count),
    ("Recalls Over Years", plot_recalls_over_years),
    ("Recall Distribution by Component", plot_recall_distribution_by_component),
    ("Year Boxplot by Make", plot_rating_boxplot_by_make),
    ("Recall Heatmap", plot_recall_heatmap),
    ("Consequence Distribution", plot_consequence_distribution),
    ("Cumulative Recalls Over Time", plot_cumulative_recalls_over_time),
    ("Dashboard Subplots", plot_dashboard_subplots),
]

INTERACTIVE_CHARTS = [
    ("Interactive Recalls by Make", interactive_recalls_by_make),
    ("Interactive Recalls Timeline", interactive_recalls_timeline),
    ("Interactive Component Treemap", interactive_component_treemap),
    ("Interactive Scatter Year vs Count", interactive_scatter_year_vs_count),
    ("Interactive Multi Layout", interactive_multi_layout),
]


def load_data(csv_path=None):
    path = csv_path or DEFAULT_CSV
    logging.info(f"Loading dataset from {path}")
    df = pd.read_csv(path)

    rename_map = {}
    if "data.make" in df.columns:
        rename_map["data.make"] = "make"
    if "data.model" in df.columns:
        rename_map["data.model"] = "model"
    if "data.year" in df.columns:
        rename_map["data.year"] = "modelYear"
    if "data.document_type" in df.columns:
        rename_map["data.document_type"] = "component"
    if "data.description" in df.columns:
        rename_map["data.description"] = "consequence_summary"
    if rename_map:
        df = df.rename(columns=rename_map)

    if "component" not in df.columns:
        df["component"] = "Unknown"
    if "consequence_summary" not in df.columns:
        df["consequence_summary"] = ""
    if "make" not in df.columns:
        df["make"] = "Unknown"
    if "modelYear" not in df.columns:
        df["modelYear"] = None

    df = df[df["make"].notna() & ~df["make"].isin(["Unknown", "UNKNOWN"])]
    df["component"] = df["component"].fillna("Unknown")

    logging.info(f"Loaded {len(df)} records after filtering")
    return df


def run_static_charts(df):
    logging.info(f"Generating {len(STATIC_CHARTS)} static charts")
    for name, func in STATIC_CHARTS:
        logging.info(f"  Generating: {name}")
        func(df, STATIC_DIR)
    logging.info(f"Static charts saved to {STATIC_DIR}")


def run_interactive_charts(df):
    logging.info(f"Generating {len(INTERACTIVE_CHARTS)} interactive charts")
    for name, func in INTERACTIVE_CHARTS:
        logging.info(f"  Generating: {name}")
        func(df, INTERACTIVE_DIR)
    logging.info(f"Interactive charts saved to {INTERACTIVE_DIR}")


def run_all_charts(csv_path=None):
    df = load_data(csv_path)
    run_static_charts(df)
    run_interactive_charts(df)
    logging.info("All charts generated successfully")
