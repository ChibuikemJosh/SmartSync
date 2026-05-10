from fastapi import APIRouter, File, UploadFile

from services.ocr_service import process_image_with_easyocr

router = APIRouter(prefix="/ocr", tags=["ocr"])


@router.post("/upload")
async def ocr_upload(file: UploadFile = File(...)) -> dict:
    file_bytes = await file.read()
    return process_image_with_easyocr(file_bytes)
