import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))

from utils.logger import logging
from storage.mongo import save_to_mongo
from storage.s3 import upload_file_to_s3
from api.client import fetch_all_vehicles

def run_pipeline():
    logging.info("Pipeline started")

    # Fetch data from API
    logging.info("Fetching data from NHTSA API")
    vehicles = fetch_all_vehicles(pages=3)
    logging.info(f"Fetched data for {len(vehicles)} vehicles")

    # Save to MongoDB and S3
    for vehicle in vehicles:
        # Save to MongoDB
        save_to_mongo(vehicle, "nhtsa_api")

        # Save to S3
        make = vehicle["make"]
        model = vehicle["model"]
        year = vehicle["year"]
        filename = f"recalls_{make}_{model}_{year}.json"
        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "data", "raw", "api", filename
        )
        upload_file_to_s3(file_path, filename)

    logging.info("Pipeline finished successfully")

if __name__ == "__main__":
    run_pipeline()