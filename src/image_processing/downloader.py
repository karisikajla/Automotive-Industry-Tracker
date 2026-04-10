import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')))

import requests
from src.utils.logger import logging

IMAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'raw', 'images'))

VEHICLES = [
    {"name": "audi_a4", "query": "Audi A4"},
    {"name": "volkswagen_golf", "query": "Volkswagen Golf"},
    {"name": "volkswagen_passat", "query": "Volkswagen Passat"},
    {"name": "audi_rs6", "query": "Audi RS6"},
    {"name": "volkswagen_id4", "query": "Volkswagen ID.4"},
]

def get_wikipedia_image_url(query):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": query,
        "prop": "pageimages",
        "format": "json",
        "pithumbsize": 800
    }
    headers = {"User-Agent": "ResearchBot/1.0"}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            thumbnail = page.get("thumbnail", {})
            if thumbnail:
                return thumbnail.get("source")
    except Exception as e:
        logging.error(f"Wikipedia API error for {query}: {e}")
    return None

def download_vehicle_images():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    downloaded = []
    headers = {"User-Agent": "ResearchBot/1.0"}

    for vehicle in VEHICLES:
        filename = f"{vehicle['name']}.jpg"
        filepath = os.path.join(IMAGES_DIR, filename)

        if os.path.exists(filepath):
            logging.info(f"Already exists, skipping: {filename}")
            downloaded.append(filepath)
            continue

        try:
            image_url = get_wikipedia_image_url(vehicle['query'])
            if not image_url:
                logging.warning(f"No image found for {vehicle['query']}")
                continue

            logging.info(f"Downloading: {filename} from {image_url}")
            response = requests.get(image_url, headers=headers, timeout=15)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                f.write(response.content)

            logging.info(f"Downloaded: {filename} ({len(response.content)} bytes)")
            downloaded.append(filepath)

        except Exception as e:
            logging.error(f"Failed to download {filename}: {e}")

    logging.info(f"Downloaded {len(downloaded)} images")
    return downloaded