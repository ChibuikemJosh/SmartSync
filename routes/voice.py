from fastapi import APIRouter, File, HTTPException, UploadFile

from services.voice_service import transcribe_audio_with_whisper

router = APIRouter(prefix="/voice", tags=["voice"])
MAX_AUDIO_SIZE_BYTES = 10 * 1024 * 1024
READ_CHUNK_SIZE = 1024 * 1024


async def _read_limited_file(file: UploadFile, max_bytes: int) -> bytes:
    chunks = []
    total_size = 0
    while True:
        chunk = await file.read(READ_CHUNK_SIZE)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > max_bytes:
            raise HTTPException(status_code=413, detail="Audio file is too large.")
        chunks.append(chunk)
    return b"".join(chunks)


@router.post("/upload")
async def voice_upload(file: UploadFile = File(...)) -> dict:
    if not file.content_type or not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Expected audio.")

    file_bytes = await _read_limited_file(file, MAX_AUDIO_SIZE_BYTES)

    return transcribe_audio_with_whisper(file_bytes)
