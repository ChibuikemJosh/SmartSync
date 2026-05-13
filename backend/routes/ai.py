"""
AI Processing Routes
Handles Voice-to-JSON and OCR (Image-to-JSON) processing
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel

from typing import Optional, Dict, Any
import logging
import shutil
import tempfile
import os
import uuid

from services.ai_logic import process_voice_entry, update_job_status, get_job_status
from services.database import GraphService
from services.ocr_logic import process_ledger_image

from utils.helpers import save_temp_file

from models.schemas import VoiceProcessResponse, ErrorResponse


logger = logging.getLogger(__name__)

router = APIRouter()
graph_service = GraphService()


async def run_ai_pipeline(job_id: str, user_id: str, tmp_path: str):
    try:
        final_data = process_voice_entry(tmp_path)

        if final_data:
            new_score = graph_service.log_transaction(user_id, final_data)

            update_job_status(job_id, "completed", {
                "result": final_data, 
                "new_score": new_score
            })
        else:
            update_job_status(job_id, "failed", {"error": "AI parsing failed"})

    except Exception as e:
        logger.error(f"Job {job_id} crashed: {str(e)}")
        # 4. Handle unexpected crashes
        update_job_status(job_id, "failed", {"error": "Internal Processing Error"})
    
    finally:
        # 5. Clean up the temp file so the server disk doesn't fill up
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


async def run_ocr_pipeline(job_id: str, user_id: str, tmp_path: str):
    try:
        final_data = process_ledger_image(tmp_path)

        if final_data:
            new_score = graph_service.log_transaction(user_id, final_data)

            update_job_status(job_id, "completed", {
                "result": final_data, 
                "new_score": new_score
            })
        else:
            update_job_status(job_id, "failed", {"error": "OCR parsing failed"})

    except Exception as e:
        logger.error(f"OCR Job {job_id} crashed: {str(e)}")
        update_job_status(job_id, "failed", {"error": "Internal OCR Processing Error"})
    
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.post("/process-voice")
async def process_voice(user_id: str, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    filename = file.filename or ""
    if not filename.lower().endswith(('.mp3', '.wav', '.m4a', '.ogg', '.flac', '.mpeg', '.mpga', '.mp4', '.webm')):
        raise HTTPException(status_code=400, detail="Invalid file format")

    job_id = str(uuid.uuid4()) # Generate a unique "Buzzer" ID

    update_job_status(job_id, "processing")

    tmp_path = await save_temp_file(file)

    background_tasks.add_task(run_ai_pipeline, job_id, user_id, tmp_path)

    return {"status": "accepted", "job_id": job_id}


@router.post("/process-ledger")
async def process_ledger(user_id: str, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    update_job_status(job_id, "processing")

    tmp_path = await save_temp_file(file)

    background_tasks.add_task(run_ocr_pipeline, job_id, user_id, tmp_path)

    return {"status": "accepted", "job_id": job_id}


@router.get("/status/{job_id}")
async def check_status(job_id: str):
    status = get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job ID not found")
    return status