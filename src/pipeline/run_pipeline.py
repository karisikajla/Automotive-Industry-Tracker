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
from scraping.scraper import run_scraper
from scraping.dynamic_scraper import run_dynamic_scraper
from ocr.ocr_utils import run_ocr_pipeline
from image_processing.downloader import download_vehicle_images
from image_processing.batch import batch_process_images
from image_processing.exif_utils import process_exif_samples

def run_pipeline():
    logging.info("Pipeline started")

    # Fetch data from API
    logging.info("Fetching data from NHTSA API")
    vehicles = fetch_all_vehicles(pages=3)
    logging.info(f"Fetched data for {len(vehicles)} vehicles")

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
    logging.info("Extracting PDF documents")
    pdf_results = extract_all_pdfs()
    logging.info(f"Extracted {len(pdf_results)} PDF files")

    # Extract Word documents
    logging.info("Extracting Word documents")
    word_results = extract_all_word_docs()
    logging.info(f"Extracted {len(word_results)} Word files")

    # Extract Excel files
    logging.info("Extracting Excel files")
    excel_results = extract_all_excel()
    logging.info(f"Extracted {len(excel_results)} Excel files")

    # Web scraping
    logging.info("Running web scraper")
    scraped_results = run_scraper()
    logging.info(f"Scraped {len(scraped_results)} records")

    # Dynamic scraping
    logging.info("Running dynamic scraper")
    dynamic_results = run_dynamic_scraper()
    logging.info(f"Dynamic scraped {len(dynamic_results)} records")

    # OCR
    logging.info("Running OCR pipeline")
    ocr_results = run_ocr_pipeline()
    logging.info(f"OCR processed {len(ocr_results)} files")

    # Download vehicle images
    logging.info("Downloading vehicle images")
    downloaded = download_vehicle_images()
    logging.info(f"Downloaded {len(downloaded)} images")

    # Batch process images
    logging.info("Batch processing images")
    image_results = batch_process_images()
    logging.info(f"Processed {len(image_results)} images")

    # Process EXIF samples
    logging.info("Processing EXIF samples")
    exif_results = process_exif_samples()
    logging.info(f"Processed {len(exif_results)} EXIF samples")

    logging.info("Pipeline finished successfully")

run_pipeline()