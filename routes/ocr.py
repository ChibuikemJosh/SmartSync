from fastapi import APIRouter, File, HTTPException, UploadFile

from services.ocr_service import process_image_with_easyocr

router = APIRouter(prefix="/ocr", tags=["ocr"])
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024


@router.post("/upload")
async def ocr_upload(file: UploadFile = File(...)) -> dict:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Expected an image.")

    file_bytes = await file.read(MAX_IMAGE_SIZE_BYTES + 1)
    if len(file_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="Image file is too large.")

    return process_image_with_easyocr(file_bytes)
