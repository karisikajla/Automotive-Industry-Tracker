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

def get_transcripts_collection():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["automotive_pipeline"]
    return db["transcripts"]

def save_transcript_to_mongo(transcript_result):
    try:
        collection = get_transcripts_collection()
        document = {
            "source_file": transcript_result.get("source_file"),
            "language": transcript_result.get("language"),
            "language_probability": transcript_result.get("language_probability"),
            "duration": transcript_result.get("duration"),
            "model": transcript_result.get("model"),
            "segments": transcript_result.get("segments", []),
            "segment_count": len(transcript_result.get("segments", [])),
            "stored_at": datetime.utcnow()
        }
        result = collection.insert_one(document)
        logging.info(f"Saved transcript to MongoDB with id: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        logging.error(f"MongoDB error saving transcript: {e}")
        return None

def get_transcripts_by_source(source_file):
    try:
        collection = get_transcripts_collection()
        results = list(collection.find({"source_file": source_file}))
        logging.info(f"Found {len(results)} transcripts for: {source_file}")
        return results
    except Exception as e:
        logging.error(f"MongoDB error fetching transcripts: {e}")
        return []