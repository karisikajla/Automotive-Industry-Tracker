import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))

import json
import shutil
from datetime import datetime
from utils.logger import logging

# Simulate S3 bucket locally
S3_BUCKET_NAME = "automotive-pipeline-bucket"
S3_LOCAL_PATH = "../../data/s3_bucket"

def create_bucket():
    bucket_path = os.path.join(S3_LOCAL_PATH, S3_BUCKET_NAME)
    os.makedirs(bucket_path, exist_ok=True)
    logging.info(f"S3 bucket ready: {S3_BUCKET_NAME}")
    return bucket_path

def upload_file_to_s3(file_path, file_name):
    try:
        bucket_path = create_bucket()
        destination = os.path.join(bucket_path, file_name)
        shutil.copy2(file_path, destination)
        logging.info(f"Successfully uploaded {file_name} to {S3_BUCKET_NAME}")
        return True
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return False
    except Exception as e:
        logging.error(f"Upload error: {e}")
        return False

def list_bucket():
    bucket_path = os.path.join(S3_LOCAL_PATH, S3_BUCKET_NAME)
    if not os.path.exists(bucket_path):
        logging.warning("Bucket does not exist yet")
        return []
    files = os.listdir(bucket_path)
    logging.info(f"Files in {S3_BUCKET_NAME}: {files}")
    return files

if __name__ == "__main__":
    api_folder = "../../data/raw/api"
    for filename in os.listdir(api_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(api_folder, filename)
            upload_file_to_s3(file_path, filename)
    
    files = list_bucket()
    print(f"Files in bucket: {files}")