import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))

from utils.logger import logging
from storage.mongo import save_to_mongo
from storage.s3 import upload_file_to_s3
from api.client import fetch_all_vehicles
from extraction.pdf_extractor import extract_all_pdfs
from extraction.word_extractor import extract_all_word_docs
from extraction.excel_extractor import extract_all_excel

def run_pipeline():
    logging.info("Pipeline started")

    # Fetch data from API
    logging.info("Step 1: Fetching data from NHTSA API")
    vehicles = fetch_all_vehicles(pages=3)
    logging.info(f"Fetched data for {len(vehicles)} vehicles")

    # Save to MongoDB and S3
    for vehicle in vehicles:
        save_to_mongo(vehicle, "nhtsa_api")
        make = vehicle["make"]
        model = vehicle["model"]
        year = vehicle["year"]
        filename = f"recalls_{make}_{model}_{year}.json"
        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "data", "raw", "api", filename
        )
        upload_file_to_s3(file_path, filename)

    # Extract PDF documents
    logging.info("Step 3: Extracting PDF documents")
    pdf_results = extract_all_pdfs()
    logging.info(f"Extracted {len(pdf_results)} PDF files")

    # Extract Word documents
    logging.info("Step 4: Extracting Word documents")
    word_results = extract_all_word_docs()
    logging.info(f"Extracted {len(word_results)} Word files")

    # Extract Excel files
    logging.info("Step 5: Extracting Excel files")
    excel_results = extract_all_excel()
    logging.info(f"Extracted {len(excel_results)} Excel files")

    logging.info("Pipeline finished successfully")

run_pipeline()