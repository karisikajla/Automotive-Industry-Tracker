import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))

from utils.logger import logging


def run_pipeline():
    logging.info("Pipeline started")

    logging.info("Starting Lab 12 visualizations")
    from visualization.chart_generator import run_all_charts
    run_all_charts()
    logging.info("Visualizations complete")

    logging.info("Pipeline finished successfully")


run_pipeline()
