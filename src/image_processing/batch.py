import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')))

from tqdm import tqdm
from datetime import datetime
from src.utils.logger import logging
from src.storage.mongo import save_to_mongo
from src.image_processing.processor import (
    inspect_image, resize_image, generate_thumbnail,
    generate_fixed_thumbnail, crop_image, convert_to_webp,
    convert_to_grayscale, save_optimised_jpeg,
    apply_filters, apply_enhancements
)
from src.image_processing.exif_utils import get_exif_summary

IMAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'raw', 'images'))

def process_single(filepath):
    try:
        logging.info(f"Processing: {os.path.basename(filepath)}")

        info = inspect_image(filepath)
        resized_path = resize_image(filepath)
        proportional_path = resize_image(filepath, width=800, height=600)
        thumb_path = generate_thumbnail(filepath)
        fixed_thumb_path = generate_fixed_thumbnail(filepath)
        cropped_path = crop_image(filepath)
        webp_path = convert_to_webp(filepath)
        grey_path = convert_to_grayscale(filepath)
        optimised_path = save_optimised_jpeg(filepath)
        apply_filters(filepath)
        apply_enhancements(filepath)
        exif_summary = get_exif_summary(filepath)

        metadata = {
            "file_name": os.path.basename(filepath),
            "source": "vehicle_image",
            "type": "automotive",
            "original_path": filepath,
            "resized_path": resized_path,
            "thumbnail_path": thumb_path,
            "webp_path": webp_path,
            "format": info.get("format") if info else None,
            "mode": info.get("mode") if info else None,
            "width": info.get("width") if info else None,
            "height": info.get("height") if info else None,
            "file_size_kb": info.get("file_size_kb") if info else None,
            "exif": exif_summary,
            "processed_at": datetime.utcnow().isoformat()
        }

        save_to_mongo(metadata, "image_processing")
        logging.info(f"Saved metadata to MongoDB for {os.path.basename(filepath)}")
        return metadata

    except Exception as e:
        logging.error(f"Error processing {filepath}: {e}")
        return None

def batch_process_images():
    if not os.path.exists(IMAGES_DIR):
        logging.warning(f"Images directory not found: {IMAGES_DIR}")
        return []

    image_files = [
        os.path.join(IMAGES_DIR, f)
        for f in os.listdir(IMAGES_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ]

    if not image_files:
        logging.warning("No images found to process")
        return []

    logging.info(f"Starting batch processing of {len(image_files)} images")
    results = []

    for filepath in tqdm(image_files, desc="Processing images"):
        result = process_single(filepath)
        if result:
            results.append(result)

    logging.info(f"Batch processing complete. Processed {len(results)} images")
    return results