import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))

from pymongo import MongoClient
from datetime import datetime
from utils.logger import logging

def get_collection():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["automotive_pipeline"]
    return db["raw_recalls"]

def save_to_mongo(data, source):
    try:
        collection = get_collection()
        document = {
            "data": data,
            "source": source,
            "fetched_at": datetime.utcnow(),
            "version": 1
        }
        result = collection.insert_one(document)
        logging.info(f"Saved to MongoDB with id: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        logging.error(f"MongoDB error: {e}")
        return None

if __name__ == "__main__":
    test_data = {"make": "Audi", "model": "A4", "year": 2020, "recalls": []}
    save_to_mongo(test_data, "test")
    print("Done! Check MongoDB.")