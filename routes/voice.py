from fastapi import APIRouter, File, HTTPException, UploadFile

from services.voice_service import transcribe_audio_with_whisper

router = APIRouter(prefix="/voice", tags=["voice"])
MAX_AUDIO_SIZE_BYTES = 10 * 1024 * 1024


@router.post("/upload")
async def voice_upload(file: UploadFile = File(...)) -> dict:
    if not file.content_type or not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Expected audio.")

    file_bytes = await file.read(MAX_AUDIO_SIZE_BYTES + 1)
    if len(file_bytes) > MAX_AUDIO_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="Audio file is too large.")

    return transcribe_audio_with_whisper(file_bytes)
