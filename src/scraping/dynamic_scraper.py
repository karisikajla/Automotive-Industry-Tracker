import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')))

import json
import time
import requests
from datetime import datetime
from src.utils.logger import logging
from src.storage.mongo import save_to_mongo
from src.scraping.robots_utils import HEADERS

SCRAPED_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'raw', 'scraped'))

def scrape_nhtsa_json_api(pages=3):
    logging.info("Starting dynamic scraping via NHTSA JSON API")
    all_results = []

    vehicles = [
        {"make": "Audi", "model": "A4", "year": 2020},
        {"make": "Volkswagen", "model": "Golf", "year": 2020},
        {"make": "Volkswagen", "model": "Passat", "year": 2020},
    ]

    for i, vehicle in enumerate(vehicles[:pages]):
        make = vehicle["make"]
        model = vehicle["model"]
        year = vehicle["year"]
        url = f"https://api.nhtsa.gov/recalls/recallsByVehicle?make={make}&model={model}&modelYear={year}"

        logging.info(f"Fetching JSON API page {i+1}: {url}")
        try:
            time.sleep(1.5)
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()

            record = {
                "make": make,
                "model": model,
                "year": year,
                "recalls": data.get("results", []),
                "scraped_at": datetime.utcnow().isoformat(),
                "source": url,
                "type": "json_api"
            }
            all_results.append(record)
            save_to_mongo(record, "dynamic_scraping")
            logging.info(f"Fetched {len(record['recalls'])} recalls for {make} {model}")

        except Exception as e:
            logging.error(f"Error fetching {make} {model}: {e}")

    os.makedirs(SCRAPED_DIR, exist_ok=True)
    filepath = os.path.join(SCRAPED_DIR, "dynamic_scraped.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    logging.info(f"Saved dynamic scraped JSON: {filepath}")

    return all_results

def run_dynamic_scraper():
    logging.info("Running dynamic scraper")
    results = scrape_nhtsa_json_api(pages=3)
    logging.info(f"Dynamic scraping complete. Total: {len(results)} records")
    return results