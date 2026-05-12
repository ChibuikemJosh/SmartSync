"""
AI Processing Routes
Handles Voice-to-JSON and OCR (Image-to-JSON) processing
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Depends
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
        # 4. Handle unexpected crashes
        update_job_status(job_id, "failed", {"error": str(e)})
    
    finally:
        # 5. Clean up the temp file so the server disk doesn't fill up
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.post("/process-voice")
async def process_voice(user_id: str, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    job_id = str(uuid.uuid4()) # Generate a unique "Buzzer" ID

    update_job_status(job_id, "processing")

    tmp_path = await save_temp_file(file)

    background_tasks.add_task(run_ai_pipeline, job_id, user_id, tmp_path)

    return {"status": "accepted", "job_id": job_id}


@router.post("/process-ledger")
async def handle_ledger(user_id: str, file: UploadFile = File(...)):
    # Save image temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # Run OCR -> AI -> JSON pipeline
        final_data = process_ledger_image(tmp_path)
        
        if final_data:
            # Save to Neo4j and update Trust Score
            new_score = graph_service.log_transaction(user_id, final_data)
            return {"status": "success", "data": final_data, "score": new_score}
            
        return {"status": "error", "message": "Could not read ledger photo"}
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)