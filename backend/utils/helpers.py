"""
Utility functions for common SmartSync operations
"""
import os
import shutil
import tempfile
import logging
from pathlib import Path
from fastapi import UploadFile, HTTPException, status

logger = logging.getLogger(__name__)

# Combine audio and image extensions for all AI processing
ALLOWED_EXTENSIONS = {
    '.mp3', '.wav', '.m4a', '.ogg', '.flac', '.mpeg', '.mpga', '.mp4', '.webm', # Audio
    '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp' # Images
}

async def save_temp_file(file: UploadFile) -> str:
    """
    Validates file extension and saves upload to a persistent 
    temporary file so the background worker can access it.
    """
    filename = file.filename or ""
    file_path = Path(filename)
    extension = file_path.suffix.lower()

    # 1. Validate extension
    if extension not in ALLOWED_EXTENSIONS:
        logger.warning(f"Rejected file with invalid extension: {extension}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Format {extension} no support. Use audio or clear image."
        )

    try:
        # 2. Create the temp file
        # delete=False allows the background task to pick this up after the request ends
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp:
            # Efficiently stream the uploaded file to disk
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        logger.info(f"File saved temporary: {tmp_path}")
        return tmp_path

    except Exception as e:
        logger.error(f"File system error during upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Something went wrong saving the file for processing."
        )

def cleanup_temp_file(file_path: str):
    """
    Call this in your background task 'finally' block 
    to prevent the server disk from filling up.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Successfully cleaned up temp file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to delete temp file {file_path}: {e}")