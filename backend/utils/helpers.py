"""
Utility functions for common operations
"""
import os
import shutil
import tempfile
from fastapi import UploadFile, HTTPException


async def save_temp_file(file: UploadFile) -> str:
    """
    Validates the audio extension and saves the upload to a persistent 
    temporary file for the background worker to use.
    """
    # 1. Validate extension
    filename = file.filename or ""
    allowed_extensions = ('.mp3', '.wav', '.m4a', '.ogg', '.flac', '.mpeg', '.mpga', '.mp4', '.webm')
    
    if not filename.lower().endswith(allowed_extensions):
        raise HTTPException(status_code=400, detail="Invalid audio format")
    
    # 2. Get the extension (suffix)
    suffix = os.path.splitext(filename)[1]
    
    try:
        # 3. Create the temp file. 
        # Note: delete=False is required so the file isn't deleted when the 
        # request finishes, allowing the background task to access it.
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
            
        return tmp_path
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
