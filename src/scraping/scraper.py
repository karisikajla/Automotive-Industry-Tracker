import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')))

import json
import time
from bs4 import BeautifulSoup
from datetime import datetime
from src.utils.logger import logging
from src.storage.mongo import save_to_mongo
from src.scraping.robots_utils import check_robots_txt, polite_get

BASE_URL = "https://www.autoevolution.com"
TARGET_PATH = "/cars/audi/a4/"

HTML_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'raw', 'html'))
SCRAPED_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'raw', 'scraped'))

def save_html(html, filename):
    os.makedirs(HTML_DIR, exist_ok=True)
    filepath = os.path.join(HTML_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    logging.info(f"Saved raw HTML: {filepath}")

def save_scraped_json(data, filename):
    os.makedirs(SCRAPED_DIR, exist_ok=True)
    filepath = os.path.join(SCRAPED_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logging.info(f"Saved scraped JSON: {filepath}")

def scrape_single_page(url):
    logging.info(f"Scraping single page: {url}")
    try:
        response = polite_get(url)
        html = response.text
        save_html(html, "page_1.html")

        soup = BeautifulSoup(html, "lxml")
        results = []

        items = soup.select("div.carwrap")
        for item in items:
            title = item.select_one("h2")
            description = item.select_one("p")
            link = item.select_one("a")
            record = {
                "title": title.get_text(strip=True) if title else "",
                "description": description.get_text(strip=True) if description else "",
                "link": link["href"] if link else "",
                "scraped_at": datetime.utcnow().isoformat(),
                "source": url
            }
            results.append(record)

        logging.info(f"Scraped {len(results)} items from {url}")
        return results

    except Exception as e:
        logging.error(f"Error scraping {url}: {e}")
        return []

def scrape_multiple_pages(base_url, pages=3):
    logging.info(f"Starting multi-page scraping: {pages} pages")
    all_results = []

    urls = [
        "https://www.autoevolution.com/cars/audi/a4/",
        "https://www.autoevolution.com/cars/volkswagen/golf/",
        "https://www.autoevolution.com/cars/volkswagen/passat/",
    ]

    for i, url in enumerate(urls[:pages]):
        logging.info(f"Scraping page {i+1}: {url}")
        try:
            response = polite_get(url)
            html = response.text
            save_html(html, f"page_{i+1}.html")

            soup = BeautifulSoup(html, "lxml")
            items = soup.select("div.carwrap")

            for item in items:
                title = item.select_one("h2")
                description = item.select_one("p")
                link = item.select_one("a")
                record = {
                    "title": title.get_text(strip=True) if title else "",
                    "description": description.get_text(strip=True) if description else "",
                    "link": link["href"] if link else "",
                    "scraped_at": datetime.utcnow().isoformat(),
                    "source": url,
                    "page": i+1
                }
                all_results.append(record)

        except Exception as e:
            logging.error(f"Error scraping page {i+1}: {e}")

    save_scraped_json(all_results, "scraped_results.json")

    for record in all_results:
        save_to_mongo(record, "web_scraping")

    logging.info(f"Multi-page scraping complete. Total records: {len(all_results)}")
    return all_results

def run_scraper():
    allowed = check_robots_txt(BASE_URL, TARGET_PATH)
    if not allowed:
        logging.warning("Scraping not allowed by robots.txt")
        return []

    results = scrape_multiple_pages(BASE_URL, pages=3)
    return results