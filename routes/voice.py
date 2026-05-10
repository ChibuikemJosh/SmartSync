from fastapi import APIRouter, File, HTTPException, UploadFile

from routes.upload_utils import read_limited_file
from services.voice_service import transcribe_audio_with_whisper

router = APIRouter(prefix="/voice", tags=["voice"])
MAX_AUDIO_SIZE_BYTES = 10 * 1024 * 1024


@router.post("/upload")
async def voice_upload(file: UploadFile = File(...)) -> dict:
    if not file.content_type or not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Expected audio.")

    file_bytes = await read_limited_file(
        file, MAX_AUDIO_SIZE_BYTES, too_large_detail="Audio file is too large."
    )

    return transcribe_audio_with_whisper(file_bytes)
