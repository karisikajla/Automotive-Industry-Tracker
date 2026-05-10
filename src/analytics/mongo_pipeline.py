import pandas as pd
import logging
from pymongo import MongoClient


def get_mongo_collection(uri="mongodb://localhost:27017", db_name="automotive_tracker", collection_name="raw_recalls"):
    client = MongoClient(uri)
    db = client[db_name]
    return db[collection_name]


def run_aggregation_pipeline(collection):
    pipeline = [
        {"$match": {"data.make": {"$exists": True, "$ne": None}}},
        {"$group": {
            "_id": "$data.make",
            "total_recalls": {"$sum": {"$size": {"$ifNull": ["$data.recalls", []]}}},
            "avg_version": {"$avg": "$version"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$project": {
            "_id": 0,
            "make": "$_id",
            "total_recalls": 1,
            "avg_version": 1,
            "count": 1
        }}
    ]
    results = list(collection.aggregate(pipeline))
    logging.info(f"MongoDB pipeline returned {len(results)} documents.")
    return pd.DataFrame(results)