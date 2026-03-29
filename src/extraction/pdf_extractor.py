import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')))

import pdfplumber
import chardet
from datetime import datetime
from src.utils.logger import logging
from src.storage.mongo import save_to_mongo

def detect_encoding(filepath):
    with open(filepath, "rb") as f:
        raw = f.read()
    result = chardet.detect(raw)
    encoding = result.get("encoding", "utf-8")
    logging.info(f"Detected encoding for {filepath}: {encoding}")
    return encoding

def extract_pdf(filepath):
    logging.info(f"Starting PDF extraction: {filepath}")
    result = {
        "file_name": os.path.basename(filepath),
        "document_type": "pdf",
        "source": filepath,
        "extraction_timestamp": datetime.utcnow().isoformat(),
        "extraction_library": "pdfplumber",
        "pages": []
    }

    try:
        with pdfplumber.open(filepath) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_data = {
                    "page_number": page_num,
                    "text": page.extract_text() or "",
                    "tables": page.extract_tables() or []
                }
                result["pages"].append(page_data)
                logging.info(f"Extracted page {page_num} from {os.path.basename(filepath)}")

        save_to_mongo(result, "pdf_extraction")
        logging.info(f"PDF extraction complete: {filepath}")

    except Exception as e:
        logging.error(f"Error extracting PDF {filepath}: {e}")

    return result

def extract_all_pdfs():
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
    pdf_dir = os.path.join(ROOT_DIR, "data", "raw", "pdf")
    results = []
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            filepath = os.path.join(pdf_dir, filename)
            result = extract_pdf(filepath)
            results.append(result)
    return results

if __name__ == "__main__":
    results = extract_all_pdfs()
    for r in results:
        print(f"Extracted {r['file_name']}: {len(r['pages'])} pages")