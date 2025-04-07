import os
import time
from datetime import datetime, timedelta

XLSX_FOLDER = "output"
IMAGE_FOLDER = "images"
EXPIRATION_DAYS = 30

def cleanup_old_files():
    """Deletes XLSX and zip files older than 30 days from the server."""
    now = time.time()
    expiration_time = now - (EXPIRATION_DAYS * 86400)

    # Clean up XLSX files
    for filename in os.listdir(XLSX_FOLDER):
        if filename.endswith(".xlsx"):
            file_path = os.path.join(XLSX_FOLDER, filename)
            if os.path.getctime(file_path) < expiration_time:
                os.remove(file_path)
                print(f"Deleted old XLSX file: {filename}")

    # Clean up zip files (raw, annotated, cropped)
    for filename in os.listdir(IMAGE_FOLDER):
        if filename.endswith(".zip") and (filename.startswith("images_") or filename.startswith("annotated_") or filename.startswith("cropped_")):
            file_path = os.path.join(IMAGE_FOLDER, filename)
            if os.path.getctime(file_path) < expiration_time:
                os.remove(file_path)
                print(f"Deleted old zip file: {filename}")

if __name__ == "__main__":
    cleanup_old_files()
