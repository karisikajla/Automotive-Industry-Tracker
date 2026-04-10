import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')))

from PIL import Image, ImageFilter, ImageEnhance, ImageOps
from datetime import datetime
from src.utils.logger import logging

PROCESSED_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'processed'))
RESIZED_DIR = os.path.join(PROCESSED_DIR, 'resized')
THUMBNAILS_DIR = os.path.join(PROCESSED_DIR, 'thumbnails')
WEBP_DIR = os.path.join(PROCESSED_DIR, 'webp')
CROPPED_DIR = os.path.join(PROCESSED_DIR, 'cropped')

def inspect_image(filepath):
    try:
        img = Image.open(filepath)
        file_size = os.path.getsize(filepath)
        info = {
            "file_name": os.path.basename(filepath),
            "format": img.format,
            "mode": img.mode,
            "width": img.size[0],
            "height": img.size[1],
            "file_size_bytes": file_size,
            "file_size_kb": round(file_size / 1024, 2)
        }
        logging.info(f"Inspected {info['file_name']}: {info['width']}x{info['height']} {info['format']} {info['mode']}")
        return info
    except Exception as e:
        logging.error(f"Error inspecting {filepath}: {e}")
        return None

def resize_image(filepath, width=640, height=480):
    try:
        os.makedirs(RESIZED_DIR, exist_ok=True)
        img = Image.open(filepath)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        resized = img.resize((width, height), Image.Resampling.LANCZOS)
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)
        output_path = os.path.join(RESIZED_DIR, f"{name}_resized{ext}")
        resized.save(output_path, quality=85, optimize=True)
        logging.info(f"Resized {filename} to {width}x{height}")
        return output_path
    except Exception as e:
        logging.error(f"Error resizing {filepath}: {e}")
        return None

def resize_proportional(filepath, max_size=800):
    try:
        os.makedirs(RESIZED_DIR, exist_ok=True)
        img = Image.open(filepath)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)
        output_path = os.path.join(RESIZED_DIR, f"{name}_proportional{ext}")
        img.save(output_path, quality=85, optimize=True)
        logging.info(f"Proportional resize {filename} max={max_size}")
        return output_path
    except Exception as e:
        logging.error(f"Error in proportional resize {filepath}: {e}")
        return None

def generate_thumbnail(filepath, size=(128, 128)):
    try:
        os.makedirs(THUMBNAILS_DIR, exist_ok=True)
        img = Image.open(filepath)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        thumb = img.copy()
        thumb.thumbnail(size, Image.Resampling.LANCZOS)
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)
        output_path = os.path.join(THUMBNAILS_DIR, f"{name}_thumb{ext}")
        thumb.save(output_path)
        logging.info(f"Generated thumbnail for {filename}: {thumb.size}")
        return output_path
    except Exception as e:
        logging.error(f"Error generating thumbnail {filepath}: {e}")
        return None

def generate_fixed_thumbnail(filepath, size=(200, 200)):
    try:
        os.makedirs(THUMBNAILS_DIR, exist_ok=True)
        img = Image.open(filepath)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        fitted = ImageOps.fit(img, size, Image.Resampling.LANCZOS)
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)
        output_path = os.path.join(THUMBNAILS_DIR, f"{name}_fixed_thumb{ext}")
        fitted.save(output_path)
        logging.info(f"Generated fixed thumbnail for {filename}: {size}")
        return output_path
    except Exception as e:
        logging.error(f"Error generating fixed thumbnail {filepath}: {e}")
        return None

def crop_image(filepath, box=None):
    try:
        os.makedirs(CROPPED_DIR, exist_ok=True)
        img = Image.open(filepath)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        w, h = img.size
        if box is None:
            box = (0, 0, w, h // 2)
        cropped = img.crop(box)
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)
        output_path = os.path.join(CROPPED_DIR, f"{name}_cropped{ext}")
        cropped.save(output_path)
        logging.info(f"Cropped {filename} with box {box}")
        return output_path
    except Exception as e:
        logging.error(f"Error cropping {filepath}: {e}")
        return None

def convert_to_webp(filepath, quality=80):
    try:
        os.makedirs(WEBP_DIR, exist_ok=True)
        img = Image.open(filepath)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        filename = os.path.basename(filepath)
        name = os.path.splitext(filename)[0]
        output_path = os.path.join(WEBP_DIR, f"{name}.webp")
        img.save(output_path, 'WEBP', quality=quality)
        logging.info(f"Converted {filename} to WebP")
        return output_path
    except Exception as e:
        logging.error(f"Error converting to WebP {filepath}: {e}")
        return None

def convert_to_grayscale(filepath):
    try:
        os.makedirs(RESIZED_DIR, exist_ok=True)
        img = Image.open(filepath)
        grey = img.convert('L')
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)
        output_path = os.path.join(RESIZED_DIR, f"{name}_grey{ext}")
        grey.save(output_path)
        logging.info(f"Converted {filename} to grayscale")
        return output_path
    except Exception as e:
        logging.error(f"Error converting to grayscale {filepath}: {e}")
        return None

def save_optimised_jpeg(filepath, quality=85):
    try:
        os.makedirs(RESIZED_DIR, exist_ok=True)
        img = Image.open(filepath)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        filename = os.path.basename(filepath)
        name = os.path.splitext(filename)[0]
        output_path = os.path.join(RESIZED_DIR, f"{name}_optimised.jpg")
        img.save(output_path, 'JPEG', quality=quality, optimize=True)
        logging.info(f"Saved optimised JPEG for {filename}")
        return output_path
    except Exception as e:
        logging.error(f"Error saving optimised JPEG {filepath}: {e}")
        return None

def apply_filters(filepath):
    try:
        os.makedirs(RESIZED_DIR, exist_ok=True)
        img = Image.open(filepath)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)

        blurred = img.filter(ImageFilter.GaussianBlur(radius=2))
        blurred.save(os.path.join(RESIZED_DIR, f"{name}_blurred{ext}"))

        sharpened = img.filter(ImageFilter.SHARPEN)
        sharpened.save(os.path.join(RESIZED_DIR, f"{name}_sharpened{ext}"))

        edges = img.filter(ImageFilter.FIND_EDGES)
        edges.save(os.path.join(RESIZED_DIR, f"{name}_edges{ext}"))

        logging.info(f"Applied filters to {filename}")
        return True
    except Exception as e:
        logging.error(f"Error applying filters {filepath}: {e}")
        return False

def apply_enhancements(filepath):
    try:
        os.makedirs(RESIZED_DIR, exist_ok=True)
        img = Image.open(filepath)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)

        bright = ImageEnhance.Brightness(img).enhance(1.5)
        bright.save(os.path.join(RESIZED_DIR, f"{name}_bright{ext}"))

        contrast = ImageEnhance.Contrast(img).enhance(2.0)
        contrast.save(os.path.join(RESIZED_DIR, f"{name}_contrast{ext}"))

        sharp = ImageEnhance.Sharpness(img).enhance(2.0)
        sharp.save(os.path.join(RESIZED_DIR, f"{name}_sharp{ext}"))

        logging.info(f"Applied enhancements to {filename}")
        return True
    except Exception as e:
        logging.error(f"Error applying enhancements {filepath}: {e}")
        return False