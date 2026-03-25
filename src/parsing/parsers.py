import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))

import json
import csv
import xml.etree.ElementTree as ET
from utils.logger import logging
from storage.mongo import save_to_mongo

# JSON Parsing 
def parse_json_files():
    folder = "../../data/raw/api"
    results = []
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            filepath = os.path.join(folder, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            logging.info(f"Parsed JSON: {filename}")
            save_to_mongo(data, "nhtsa_api")
            results.append(data)
    return results

# CSV Parsing 
def parse_csv_file(filepath):
    results = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                results.append(row)
        logging.info(f"Parsed CSV: {filepath}, {len(results)} rows")
    except FileNotFoundError:
        logging.error(f"CSV file not found: {filepath}")
    return results

# XML Parsing
def parse_xml_file(filepath):
    results = []
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        for child in root:
            record = {}
            for elem in child:
                record[elem.tag] = elem.text
            results.append(record)
        logging.info(f"Parsed XML: {filepath}, {len(results)} records")
    except FileNotFoundError:
        logging.error(f"XML file not found: {filepath}")
    return results

# Generate sample CSV
def generate_sample_csv():
    os.makedirs("../../data/raw/csv", exist_ok=True)
    filepath = "../../data/raw/csv/sample.csv"
    rows = [
        {"make": "Audi", "model": "A4", "year": 2020, "recall_count": 3},
        {"make": "Volkswagen", "model": "Golf", "year": 2020, "recall_count": 2},
        {"make": "Volkswagen", "model": "Passat", "year": 2020, "recall_count": 3},
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["make", "model", "year", "recall_count"])
        writer.writeheader()
        writer.writerows(rows)
    logging.info(f"Generated sample CSV: {filepath}")

# Generate sample XML
def generate_sample_xml():
    os.makedirs("../../data/raw/xml", exist_ok=True)
    filepath = "../../data/raw/xml/sample.xml"
    root = ET.Element("vehicles")
    vehicles = [
        {"make": "Audi", "model": "A4", "year": "2020"},
        {"make": "Volkswagen", "model": "Golf", "year": "2020"},
        {"make": "Volkswagen", "model": "Passat", "year": "2020"},
    ]
    for v in vehicles:
        vehicle = ET.SubElement(root, "vehicle")
        for key, value in v.items():
            child = ET.SubElement(vehicle, key)
            child.text = value
    tree = ET.ElementTree(root)
    tree.write(filepath, encoding="unicode", xml_declaration=True)
    logging.info(f"Generated sample XML: {filepath}")

if __name__ == "__main__":
    generate_sample_csv()
    generate_sample_xml()
    parse_json_files()
    parse_csv_file("../../data/raw/csv/sample.csv")
    parse_xml_file("../../data/raw/xml/sample.xml")