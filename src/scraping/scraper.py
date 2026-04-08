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

HTML_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'raw', 'html'))
SCRAPED_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'raw', 'scraped'))

def generate_local_html():
    os.makedirs(HTML_DIR, exist_ok=True)
   
    pages = [
        {
            "filename": "page_1.html",
            "cars": [
                {"title": "Audi A4 2020", "description": "Luxury sedan with 2.0L TFSI engine, 190hp. Known for premium interior and advanced driver assistance.", "price": "$39,900"},
                {"title": "Audi A4 2019", "description": "Previous generation A4 with quattro all-wheel drive. Excellent safety ratings from NHTSA.", "price": "$36,500"},
                {"title": "Audi A4 2018", "description": "Reliable executive sedan. NHTSA recall issued for airbag inflator replacement.", "price": "$33,200"},
            ]
        },
        {
            "filename": "page_2.html",
            "cars": [
                {"title": "Volkswagen Golf 2020", "description": "Compact hatchback with 1.4L TSI engine. Popular choice in European markets.", "price": "$23,195"},
                {"title": "Volkswagen Golf 2019", "description": "Award-winning hatchback. NHTSA recall for brake system defect affecting 8,200 units.", "price": "$21,500"},
                {"title": "Volkswagen Golf GTI 2020", "description": "Performance variant with 228hp turbocharged engine and sport suspension.", "price": "$29,995"},
            ]
        },
        {
            "filename": "page_3.html",
            "cars": [
                {"title": "Volkswagen Passat 2020", "description": "Midsize sedan with spacious interior. NHTSA recall for fuel pump defect.", "price": "$24,990"},
                {"title": "Volkswagen Passat 2019", "description": "Business-class sedan with advanced connectivity features and comfort.", "price": "$22,800"},
                {"title": "Skoda Octavia 2020", "description": "Czech-made sedan offering exceptional value. Part of VW Group platform.", "price": "$19,990"},
            ]
        }
    ]
   
    for page in pages:
        html_content = f"""<!DOCTYPE html>
<html>
<head><title>Automotive Recall Tracker</title></head>
<body>
<h1>Automotive Industry Tracker - Vehicle Listings</h1>
"""
        for car in page["cars"]:
            html_content += f"""
<div class="carwrap">
    <h2>{car["title"]}</h2>
    <p>{car["description"]}</p>
    <span class="price">{car["price"]}</span>
    <a href="/cars/{car["title"].lower().replace(" ", "-")}">View Details</a>
</div>
"""
        html_content += "</body></html>"
       
        filepath = os.path.join(HTML_DIR, page["filename"])
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        logging.info(f"Generated local HTML: {filepath}")

def scrape_local_html():
    logging.info("Starting local HTML scraping")
    all_results = []

    for i in range(1, 4):
        filename = f"page_{i}.html"
        filepath = os.path.join(HTML_DIR, filename)
       
        if not os.path.exists(filepath):
            logging.warning(f"HTML file not found: {filepath}")
            continue

        logging.info(f"Scraping local page {i}: {filename}")
       
        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()

        soup = BeautifulSoup(html, "lxml")
        items = soup.select("div.carwrap")

        for item in items:
            title = item.select_one("h2")
            description = item.select_one("p")
            price = item.select_one("span.price")
            link = item.select_one("a")
           
            record = {
                "title": title.get_text(strip=True) if title else "",
                "description": description.get_text(strip=True) if description else "",
                "price": price.get_text(strip=True) if price else "",
                "link": link["href"] if link else "",
                "scraped_at": datetime.utcnow().isoformat(),
                "source": f"local_html/page_{i}.html",
                "page": i
            }
            all_results.append(record)
            logging.info(f"Scraped: {record['title']}")

    os.makedirs(SCRAPED_DIR, exist_ok=True)
    filepath = os.path.join(SCRAPED_DIR, "scraped_results.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    logging.info(f"Saved scraped JSON: {filepath}")

    for record in all_results:
        save_to_mongo(record, "web_scraping")

    logging.info(f"Local scraping complete. Total records: {len(all_results)}")
    return all_results

def run_scraper():
    logging.info("Running web scraper")
    generate_local_html()
    results = scrape_local_html()
    return results