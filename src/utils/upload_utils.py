import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')))

from dotenv import load_dotenv
load_dotenv()

from src.utils.logger import logging

def authenticate_drive():
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        import pickle

        SCOPES = [os.getenv("SCOPES", "https://www.googleapis.com/auth/drive.file")]
        TOKEN_PATH = "token.pickle"
        CLIENT_SECRET_FILE = os.getenv("CLIENT_SECRET_FILE", "credentials.json")

        creds = None
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, "wb") as token:
                pickle.dump(creds, token)

        logging.info("Google Drive authenticated successfully")
        return creds

    except Exception as e:
        logging.error(f"Google Drive authentication error: {e}")
        return None

def upload_image(filepath, folder_id=None):
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        if folder_id is None:
            folder_id = os.getenv("FOLDER_ID")

        creds = authenticate_drive()
        if not creds:
            logging.error("Could not authenticate with Google Drive")
            return None

        service = build("drive", "v3", credentials=creds)
        filename = os.path.basename(filepath)

        file_metadata = {"name": filename}
        if folder_id:
            file_metadata["parents"] = [folder_id]

        media = MediaFileUpload(filepath, resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()

        file_id = file.get("id")
        logging.info(f"Uploaded {filename} to Google Drive. File ID: {file_id}")
        return file_id

    except Exception as e:
        logging.error(f"Error uploading {filepath} to Google Drive: {e}")
        return None

def upload_batch(filepaths, folder_id=None):
    if folder_id is None:
        folder_id = os.getenv("FOLDER_ID")

    logging.info(f"Starting batch upload of {len(filepaths)} files to Google Drive")
    uploaded = []

    for filepath in filepaths:
        if filepath and os.path.exists(filepath):
            file_id = upload_image(filepath, folder_id)
            if file_id:
                uploaded.append({"filepath": filepath, "file_id": file_id})
        else:
            logging.warning(f"File not found, skipping: {filepath}")

    logging.info(f"Uploaded {len(uploaded)} files to Google Drive")
    return uploaded