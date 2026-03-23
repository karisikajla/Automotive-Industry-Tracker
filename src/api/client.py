import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))

import requests
import json
import time
from dotenv import load_dotenv
from utils.logger import logging

load_dotenv()

BASE_URL = os.getenv("NHTSA_BASE_URL", "https://api.nhtsa.gov")

VEHICLES = [
    {"make": "Audi", "model": "A4", "year": 2020},
    {"make": "Volkswagen", "model": "Golf", "year": 2020},
    {"make": "Volkswagen", "model": "Passat", "year": 2020},
]

def fetch_recalls(make, model, year):
    url = f"{BASE_URL}/recalls/recallsByVehicle?make={make}&model={model}&modelYear={year}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        logging.info(f"Fetched recalls for {make} {model} {year}")
        return data.get("results", [])
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error for {make} {model}: {e}")
        return []
    except requests.exceptions.ConnectionError:
        logging.error(f"Connection error for {make} {model}")
        return []
    except requests.exceptions.Timeout:
        logging.error(f"Timeout for {make} {model}")
        return []

def fetch_all_vehicles(pages=3):
    all_results = []
    os.makedirs("../../data/raw/api", exist_ok=True)

    for i, vehicle in enumerate(VEHICLES[:pages]):
        make = vehicle["make"]
        model = vehicle["model"]
        year = vehicle["year"]

        recalls = fetch_recalls(make, model, year)
        
        page_data = {
            "make": make,
            "model": model,
            "year": year,
            "recalls": recalls
        }
        
        all_results.append(page_data)

        filename = f"../../data/raw/api/recalls_{make}_{model}_{year}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(page_data, f, indent=2)
        logging.info(f"Saved {filename}")

        time.sleep(0.5)

    return all_results

if __name__ == "__main__":
    results = fetch_all_vehicles(pages=3)
    print(f"Fetched data for {len(results)} vehicles.")
    for vehicle in results:
        print(f"{vehicle['make']} {vehicle['model']}: {len(vehicle['recalls'])} recalls")