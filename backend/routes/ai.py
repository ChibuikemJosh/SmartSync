"""
AI Processing Routes
Handles Voice-to-JSON and OCR (Image-to-JSON) processing
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import tempfile
import os
from services.ai_logic import process_voice_entry
from services.database import GraphService

logger = logging.getLogger(__name__)

router = APIRouter()
graph_service = GraphService()

@router.post("/process-voice")
async def process_voice(user_id: str, file: UploadFile = File(...)):
    # 1. (Future step) Convert Audio to Text using Whisper
    # For now, let's assume we have the text
    try:
        filename = file.filename or ""
        if not filename.endswith(('.mp3', '.wav', '.m4a', '.ogg', '.flac', '.mpeg', '.mpga', '.mp4', '.webm')):
            raise HTTPException(status_code=400, detail="Invalid audio format")
        
        # 2. Save uploaded file to a temporary path and pass the path to process_voice_entry
        suffix = os.path.splitext(filename)[1] or ""
        tmp_path = None
        try:
            content = await file.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            structured_data = process_voice_entry(tmp_path)
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    logger.warning(f"Could not remove temp file {tmp_path}")

        if not structured_data:
            return {"error": "AI could not parse the voice note"}

        # 3. Save to Neo4j and update Score
        result = graph_service.log_transaction(user_id, structured_data)
    
        return {
            "status": "success",
            "data": structured_data,
            "new_trust_score": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing voice: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process voice file")
    

class VoiceProcessResponse(BaseModel):
    """Response model for voice processing"""
    status: str
    transaction_data: Dict[str, Any]
    confidence: float
    raw_text: str


class OCRProcessResponse(BaseModel):
    """Response model for OCR processing"""
    status: str
    extracted_data: Dict[str, Any]
    confidence: float
    image_text: str


@router.post("/process-ocr", response_model=OCRProcessResponse)
async def process_ocr(file: UploadFile = File(...)):
    """
    Extract structured data from ledger images
    Image-to-JSON processing for paper ledger digitization
    
    Args:
        file: Image file containing the physical ledger
        
    Returns:
        OCRProcessResponse with extracted data
    """
    try:
        filename = file.filename or ""
        if not filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        logger.info(f"Processing OCR file: {file.filename}")
        
        # TODO: Integrate with OCR service (e.g., Tesseract, Google Cloud Vision)
        # For now, returning mock data
        
        return OCRProcessResponse(
            status="success",
            extracted_data={
                "date": "2026-05-10",
                "entries": [
                    {"description": "Morning Sales", "amount": 5000.00},
                    {"description": "Afternoon Stock", "amount": 3000.00},
                    {"description": "Evening Sales", "amount": 2500.00}
                ],
                "total": 10500.00
            },
            confidence=0.87,
            image_text="May 10, 2026 - Morning Sales: 5000 | Afternoon Stock: 3000 | Evening Sales: 2500"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing OCR: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process image")


@router.get("/voice-status/{job_id}")
async def get_voice_status(job_id: str):
    """
    Get the status of a voice processing job
    
    Args:
        job_id: The ID of the voice processing job
        
    Returns:
        Current status of the job
    """
    try:
        logger.info(f"Checking voice job status: {job_id}")
        # TODO: Implement job tracking
        return {
            "status": "completed",
            "job_id": job_id,
            "progress": 100
        }
    except Exception as e:
        logger.error(f"Error checking voice status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check job status")


@router.get("/ocr-status/{job_id}")
async def get_ocr_status(job_id: str):
    """
    Get the status of an OCR processing job
    
    Args:
        job_id: The ID of the OCR processing job
        
    Returns:
        Current status of the job
    """
    try:
        logger.info(f"Checking OCR job status: {job_id}")
        # TODO: Implement job tracking
        return {
            "status": "completed",
            "job_id": job_id,
            "progress": 100
        }
    except Exception as e:
        logger.error(f"Error checking OCR status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check job status")

