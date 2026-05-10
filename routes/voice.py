from fastapi import APIRouter, File, UploadFile

from services.voice_service import transcribe_audio_with_whisper

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/upload")
async def voice_upload(file: UploadFile = File(...)) -> dict:
    file_bytes = await file.read()
    return transcribe_audio_with_whisper(file_bytes)
