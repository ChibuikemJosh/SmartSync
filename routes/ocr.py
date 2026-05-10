from fastapi import APIRouter, File, HTTPException, UploadFile

from services.ocr_service import process_image_with_easyocr

router = APIRouter(prefix="/ocr", tags=["ocr"])
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
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
            raise HTTPException(status_code=413, detail="Image file is too large.")
        chunks.append(chunk)
    return b"".join(chunks)


@router.post("/upload")
async def ocr_upload(file: UploadFile = File(...)) -> dict:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Expected an image.")

    file_bytes = await _read_limited_file(file, MAX_IMAGE_SIZE_BYTES)

    return process_image_with_easyocr(file_bytes)
