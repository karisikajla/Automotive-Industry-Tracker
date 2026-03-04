# Automotive Industry Tracker

## 1. Project Overview

The goal of this project is to collect automotive data from different sources and formats, clean it up, and combine it into something useful — a simple tool where you can look up a car model and see its price range, known recalls, and key specs in one place.

Think of it like a personal used-car research tool. Instead of spending an hour googling, the pipeline does the boring work for you.


## 2. Data Sources & Types

We will use four main sources:

**The "Safety" data (NHTSA API):** The US government has a free API that lists every recall and safety complaint ever filed for a car model.

**The "Market" data (Web Scraping):** Used car listings from Cars.com — prices, mileage, and the text descriptions written by dealers.

**The "Specs" data (PDF files):** Car manufacturers publish official spec sheets as PDFs (engine size, weight, fuel consumption, etc.).

**The "Sales" data (Excel/CSV):** The OICA organisation publishes yearly global car sales statistics as Excel files.


## 3. Pipeline Architecture

**Step 1 — Collection:** Gather data from the API, scrape the web pages, and read the local PDF/Excel files.

**Step 2 — Processing:** Parse and clean each data type so it's in a usable format.

**Step 3 — Storage:** Save everything in one place so it can be searched and compared.

**Step 4 — Output:** A simple interface where you can search by car model and see all the data combined.

```
NHTSA API ──────┐
Cars.com scrape ─┤──► collect & process ──► storage ──► search & display
PDF spec sheets ─┤
Excel sales data ┘
```


## 4. Expected Challenges

**Scraping getting blocked:** Cars.com might block our script if we send too many requests too fast.

**Bad PDF quality:** Some spec sheets are scanned images rather than real text, so we'll need OCR to read them.

**Same car, different names:** The API might call it "VOLKSWAGEN GOLF" while the listing says "VW Golf 1.6 TDI". We'll need to handle that before combining data from different sources.


## 5. Success Criteria

- [ ] Type in a car model and get back its recall history, average price, and basic specs — all from different sources, combined in one place.
- [ ] A scanned PDF spec sheet is successfully read by the program and returns plain text (e.g. engine size, fuel consumption).
- [ ] The data is searchable — for example, filtering only cars with no open recalls.


