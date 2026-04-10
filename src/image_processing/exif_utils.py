import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')))

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime
from src.utils.logger import logging

EXIF_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'raw', 'exif_samples'))

def extract_exif(filepath):
    try:
        img = Image.open(filepath)
        exif_data = img.getexif()
        if not exif_data:
            logging.warning(f"No EXIF data found in {filepath}")
            return {}

        result = {}
        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)
            result[tag_name] = str(value)

        logging.info(f"Extracted {len(result)} EXIF tags from {os.path.basename(filepath)}")
        return result
    except Exception as e:
        logging.error(f"Error extracting EXIF from {filepath}: {e}")
        return {}

def extract_gps(filepath):
    try:
        img = Image.open(filepath)
        exif_data = img.getexif()
        if not exif_data:
            return {}

        gps_ifd = exif_data.get_ifd(0x8825)
        if not gps_ifd:
            logging.warning(f"No GPS data in {filepath}")
            return {}

        gps_data = {}
        for key, val in gps_ifd.items():
            tag_name = GPSTAGS.get(key, key)
            gps_data[tag_name] = str(val)

        logging.info(f"Extracted GPS data from {os.path.basename(filepath)}")
        return gps_data
    except Exception as e:
        logging.error(f"Error extracting GPS from {filepath}: {e}")
        return {}

def get_exif_summary(filepath):
    try:
        exif = extract_exif(filepath)
        gps = extract_gps(filepath)

        summary = {
            "file_name": os.path.basename(filepath),
            "camera_make": exif.get("Make", "Unknown"),
            "camera_model": exif.get("Model", "Unknown"),
            "date_taken": exif.get("DateTimeOriginal", exif.get("DateTime", "Unknown")),
            "exposure_time": exif.get("ExposureTime", "Unknown"),
            "aperture": exif.get("FNumber", "Unknown"),
            "iso": exif.get("ISOSpeedRatings", "Unknown"),
            "focal_length": exif.get("FocalLength", "Unknown"),
            "orientation": exif.get("Orientation", "Unknown"),
            "gps": gps if gps else "No GPS data",
            "extracted_at": datetime.utcnow().isoformat()
        }

        logging.info(f"EXIF summary for {os.path.basename(filepath)}: {summary['camera_make']} {summary['camera_model']}")
        return summary
    except Exception as e:
        logging.error(f"Error getting EXIF summary {filepath}: {e}")
        return {}

def strip_exif(filepath, output_dir=None):
    try:
        if output_dir is None:
            output_dir = EXIF_DIR
        os.makedirs(output_dir, exist_ok=True)

        img = Image.open(filepath)
        clean = Image.new(img.mode, img.size)
        clean.putdata(list(img.getdata()))

        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)
        output_path = os.path.join(output_dir, f"{name}_clean{ext}")
        clean.save(output_path)

        logging.info(f"Stripped EXIF from {filename} → {output_path}")
        return output_path
    except Exception as e:
        logging.error(f"Error stripping EXIF from {filepath}: {e}")
        return None

def process_exif_samples():
    results = []
    if not os.path.exists(EXIF_DIR):
        logging.warning(f"EXIF samples directory not found: {EXIF_DIR}")
        return results

    for filename in os.listdir(EXIF_DIR):
        if filename.endswith((".jpg", ".jpeg", ".JPG", ".JPEG")):
            filepath = os.path.join(EXIF_DIR, filename)
            summary = get_exif_summary(filepath)
            if summary:
                results.append(summary)
                strip_exif(filepath)

    logging.info(f"Processed {len(results)} EXIF samples")
    return results