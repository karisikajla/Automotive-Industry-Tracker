import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))

import numpy as np
from utils.logger import logging

def create_arrays():
    recall_counts = np.array([12, 5, 23, 8, 15, 3, 19, 7], dtype=np.int32)
    ratings = np.zeros(8, dtype=np.float32)
    flags = np.ones(8, dtype=np.bool_)
    years = np.arange(2017, 2025, dtype=np.int32)
    score_range = np.linspace(0.0, 10.0, 8)
    rng = np.random.default_rng(42)
    popularity_scores = rng.uniform(10.0, 500.0, size=8).astype(np.float32)
    vehicle_matrix = np.array([
        [2020, 4, 8.5, 120.0],
        [2021, 2, 7.2, 95.0],
        [2022, 5, 9.1, 210.0],
        [2023, 1, 6.8, 55.0],
        [2019, 3, 8.0, 180.0],
        [2021, 6, 7.5, 300.0],
        [2022, 2, 9.3, 410.0],
        [2020, 4, 6.5, 88.0],
    ], dtype=np.float32)

    logging.info("NumPy arrays created using 5 methods")

    print("Array Creation")
    print(f"recall_counts  -> shape={recall_counts.shape}, dtype={recall_counts.dtype}, ndim={recall_counts.ndim}")
    print(f"ratings        -> shape={ratings.shape}, dtype={ratings.dtype}, ndim={ratings.ndim}")
    print(f"years          -> shape={years.shape}, dtype={years.dtype}, ndim={years.ndim}")
    print(f"popularity     -> shape={popularity_scores.shape}, dtype={popularity_scores.dtype}, ndim={popularity_scores.ndim}")
    print(f"vehicle_matrix -> shape={vehicle_matrix.shape}, dtype={vehicle_matrix.dtype}, ndim={vehicle_matrix.ndim}")

    return recall_counts, ratings, years, popularity_scores, vehicle_matrix

def vectorized_operations(recall_counts, popularity_scores, vehicle_matrix):
    print("\nVectorized Operations (no loops)")

    normalized_recalls = recall_counts / recall_counts.max()
    log_popularity = np.log1p(popularity_scores)
    scaled_scores = vehicle_matrix[:, 2] * 10

    print(f"Recall counts mean     : {recall_counts.mean():.2f}")
    print(f"Recall counts std      : {recall_counts.std():.2f}")
    print(f"Recall counts min/max  : {recall_counts.min()} / {recall_counts.max()}")
    print(f"Popularity mean        : {popularity_scores.mean():.2f}")
    print(f"Popularity median      : {np.median(popularity_scores):.2f}")
    print(f"Log popularity         : {log_popularity[:3]}")
    print(f"Normalized recalls     : {normalized_recalls[:3]}")
    print(f"Scaled scores (x10)    : {scaled_scores[:3]}")

    high_recall = recall_counts[recall_counts > 10]
    print(f"High recall counts (>10): {high_recall}")

    avg_rating = vehicle_matrix[:, 2].mean()
    above_avg = vehicle_matrix[vehicle_matrix[:, 2] > avg_rating]
    print(f"Vehicles above avg rating ({avg_rating:.2f}): {len(above_avg)}")

    logging.info("Vectorized operations complete")
    return normalized_recalls, log_popularity

def run_numpy_analysis():
    logging.info("Starting NumPy analysis")
    recall_counts, ratings, years, popularity_scores, vehicle_matrix = create_arrays()
    normalized_recalls, log_popularity = vectorized_operations(recall_counts, popularity_scores, vehicle_matrix)
    logging.info("NumPy analysis complete")
    return {
        "recall_counts": recall_counts,
        "popularity_scores": popularity_scores,
        "vehicle_matrix": vehicle_matrix,
        "normalized_recalls": normalized_recalls,
        "log_popularity": log_popularity
    }

if __name__ == "__main__":
    run_numpy_analysis()