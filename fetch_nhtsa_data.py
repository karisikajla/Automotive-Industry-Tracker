import requests
import json
import os

# Vehicles to fetch recall data for
vehicles = [
    {"make": "AUDI",       "model": "A4",         "year": "2022"},
    {"make": "VOLKSWAGEN", "model": "GOLF",        "year": "2022"},
    {"make": "SKODA",      "model": "OCTAVIA",     "year": "2022"},
    {"make": "CUPRA",      "model": "FORMENTOR",   "year": "2022"},
]

# Create output folder if it doesn't exist
os.makedirs("data/raw/nhtsa", exist_ok=True)

for v in vehicles:
    make  = v["make"]
    model = v["model"]
    year  = v["year"]

    url = (
        f"https://api.nhtsa.gov/recalls/recallsByVehicle"
        f"?make={make}&model={model}&modelYear={year}"
    )

    print(f"Fetching: {make} {model} {year} ...")

    response = requests.get(url)
    data = response.json()

    # Save response as JSON file (e.g. recall_audi_a4.json)
    filename = f"data/raw/nhtsa/recall_{make.lower()}_{model.lower()}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    count = data.get("Count", 0)
    print(f"  Saved: {filename}  ({count} recalls found)")

print("\nDone! Check the data/raw/nhtsa/ folder.")
