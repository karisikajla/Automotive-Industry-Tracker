import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')))

import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
from datetime import datetime
from src.utils.logger import logging
from src.storage.mongo import save_to_mongo

IMAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'raw', 'images'))
SCANNED_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'raw', 'scanned'))

def preprocess_image(image):
    image = image.convert("L")
    image = image.filter(ImageFilter.SHARPEN)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    return image

def ocr_image(filepath):
    logging.info(f"Starting OCR on image: {filepath}")
    try:
        image = Image.open(filepath)

        raw_text = pytesseract.image_to_string(image)
        logging.info(f"Raw OCR complete for {os.path.basename(filepath)}")

        preprocessed = preprocess_image(image)
        processed_text = pytesseract.image_to_string(preprocessed)
        logging.info(f"Preprocessed OCR complete for {os.path.basename(filepath)}")

        result = {
            "file_name": os.path.basename(filepath),
            "document_type": "image_ocr",
            "source": filepath,
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "extraction_library": "pytesseract",
            "raw_text": raw_text,
            "processed_text": processed_text
        }

        save_to_mongo(result, "ocr_image")
        logging.info(f"OCR image saved to MongoDB: {filepath}")
        return result

    except Exception as e:
        logging.error(f"Error in OCR image {filepath}: {e}")
        return None

def ocr_scanned_pdf(filepath):
    logging.info(f"Starting OCR on scanned PDF: {filepath}")
    try:
        from pdf2image import convert_from_path
        pages = convert_from_path(filepath)
        all_pages = []

        for page_num, page_image in enumerate(pages, start=1):
            preprocessed = preprocess_image(page_image)
            text = pytesseract.image_to_string(preprocessed)
            page_data = {
                "page_number": page_num,
                "text": text
            }
            all_pages.append(page_data)
            logging.info(f"OCR page {page_num} of {os.path.basename(filepath)}")

        result = {
            "file_name": os.path.basename(filepath),
            "document_type": "scanned_pdf_ocr",
            "source": filepath,
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "extraction_library": "pytesseract+pdf2image",
            "pages": all_pages
        }

        save_to_mongo(result, "ocr_scanned_pdf")
        logging.info(f"Scanned PDF OCR saved to MongoDB: {filepath}")
        return result

    except Exception as e:
        logging.error(f"Error in OCR scanned PDF {filepath}: {e}")
        return None

def run_ocr_pipeline():
    results = []

    for filename in os.listdir(IMAGES_DIR):
        if filename.endswith((".png", ".jpg", ".jpeg")):
            filepath = os.path.join(IMAGES_DIR, filename)
            result = ocr_image(filepath)
            if result:
                results.append(result)

    for filename in os.listdir(SCANNED_DIR):
        if filename.endswith(".pdf"):
            filepath = os.path.join(SCANNED_DIR, filename)
            result = ocr_scanned_pdf(filepath)
            if result:
                results.append(result)

    logging.info(f"OCR pipeline complete. Processed {len(results)} files")
    return results