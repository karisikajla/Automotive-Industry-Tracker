import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))

import pandas as pd
from pymongo import MongoClient
from utils.logger import logging

ANALYTICS_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "processed", "analytics"))

def get_mongo_client():
    return MongoClient("mongodb://localhost:27017/")

def load_from_mongodb():
    logging.info("Loading data from MongoDB")
    client = get_mongo_client()
    db = client["automotive_pipeline"]
    records = []
    for collection_name in db.list_collection_names():
        collection = db[collection_name]
        for doc in collection.find():
            doc["_collection"] = collection_name
            doc.pop("_id", None)
            records.append(doc)
    df = pd.json_normalize(records)
    logging.info(f"Loaded {len(df)} records from MongoDB across {len(db.list_collection_names())} collections")
    client.close()
    return df

def save_to_csv(df, filename="raw_export.csv"):
    os.makedirs(ANALYTICS_DIR, exist_ok=True)
    path = os.path.join(ANALYTICS_DIR, filename)
    df.to_csv(path, index=False)
    logging.info(f"Saved DataFrame to CSV: {path}")
    return path

def load_from_csv(filename="raw_export.csv"):
    path = os.path.join(ANALYTICS_DIR, filename)
    if not os.path.exists(path):
        logging.warning(f"CSV file not found: {path}")
        return None
    df = pd.read_csv(path)
    logging.info(f"Loaded CSV: {path}, shape={df.shape}")
    return df

def load_chunks(filename="raw_export.csv", chunksize=100):
    path = os.path.join(ANALYTICS_DIR, filename)
    if not os.path.exists(path):
        logging.warning(f"CSV file not found: {path}")
        return None
    logging.info(f"Loading CSV in chunks of {chunksize}: {path}")
    return pd.read_csv(path, chunksize=chunksize)

def compute_global_mean_rating(filename="raw_export.csv", chunksize=100):
    chunks = load_chunks(filename, chunksize)
    if chunks is None:
        return None
    total_sum = 0.0
    total_count = 0
    rating_col = None
    for chunk in chunks:
        for col in ["data.nhtsa_rating", "rating", "vote_average", "score"]:
            if col in chunk.columns:
                rating_col = col
                break
        if rating_col:
            valid = pd.to_numeric(chunk[rating_col], errors="coerce").dropna()
            total_sum += valid.sum()
            total_count += len(valid)
    if total_count == 0:
        logging.warning("No rating column found or no valid values")
        return None
    mean = total_sum / total_count
    logging.info(f"Global mean rating ({rating_col}): {mean:.4f} from {total_count} records")
    return mean

def process_chunks_per_source(filename="raw_export.csv", chunksize=100):
    chunks = load_chunks(filename, chunksize)
    if chunks is None:
        return {}
    accumulator = {}
    for chunk in chunks:
        if "_collection" not in chunk.columns:
            continue
        for source, group in chunk.groupby("_collection"):
            if source not in accumulator:
                accumulator[source] = {"count": 0}
            accumulator[source]["count"] += len(group)
    logging.info(f"Processed chunks per source: {list(accumulator.keys())}")
    return accumulator

def optimize_dtypes(df):
    before_mb = df.memory_usage(deep=True).sum() / 1024 ** 2
    for col in df.select_dtypes(include=["float64"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="float")
    for col in df.select_dtypes(include=["int64"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="integer")
    for col in df.select_dtypes(include=["object"]).columns:
        try:
            if df[col].apply(lambda x: not isinstance(x, (list, dict))).all():
                if df[col].nunique() / max(len(df), 1) < 0.5:
                    df[col] = df[col].astype("category")
        except Exception:
            pass
    after_mb = df.memory_usage(deep=True).sum() / 1024 ** 2
    reduction = before_mb - after_mb
    logging.info(f"Memory before: {before_mb:.2f} MB, after: {after_mb:.2f} MB, reduction: {reduction:.2f} MB")
    print(f"Memory before optimisation : {before_mb:.2f} MB")
    print(f"Memory after optimisation  : {after_mb:.2f} MB")
    print(f"Reduction                  : {reduction:.2f} MB")
    return df

if __name__ == "__main__":
    df = load_from_mongodb()
    print(f"Shape: {df.shape}")
    path = save_to_csv(df)
    print(f"Saved to: {path}")
    mean = compute_global_mean_rating()
    print(f"Global mean rating: {mean}")
    sources = process_chunks_per_source()
    print(f"Sources: {sources}")
    df = optimize_dtypes(df)