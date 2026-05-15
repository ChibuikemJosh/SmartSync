"""
AI Processing Routes
Handles Voice-to-JSON and OCR (Image-to-JSON) processing
"""
import logging
import os
import uuid
from typing import Callable, Any

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Depends
from models.schemas import VoiceTransaction, VoiceProcessResponse
from services.ai_logic import process_voice_entry, update_job_status, get_job_status
from services.database import GraphService
from services.ocr_logic import process_ledger_image
from utils.dependencies import get_current_user
from utils.helpers import save_temp_file

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["AI Processing"])

# Constants
SUPPORTED_AUDIO = {'.mp3', '.wav', '.m4a', '.ogg', '.flac', '.mpeg', '.mpga', '.mp4', '.webm'}
SUPPORTED_IMAGES = {'.jpg', '.jpeg', '.png', '.webp'}

# --- Background Task Wrappers ---

async def run_pipeline_task(
    job_id: str, 
    user_id: str, 
    tmp_path: str, 
    processor_func: Callable[[str], Any],
    service_name: str
):
    """Generic background worker to handle AI/OCR logic and cleanup."""
    try:
        # If it's OCR, we might need bytes; for voice, usually the path.
        # Adjusted to handle both based on your existing logic.
        if service_name == "OCR":
            with open(tmp_path, "rb") as f:
                result = processor_func(f.read())
        else:
            result = processor_func(tmp_path)

        if result:
            update_job_status(job_id, "completed", {
                "result": result,
                "message": f"{service_name} processing complete. Please review."
            })
        else:
            update_job_status(job_id, "failed", {"error": f"{service_name} parsing failed"})

    except Exception as e:
        logger.error(f"{service_name} Job {job_id} failed: {str(e)}")
        update_job_status(job_id, "failed", {"error": "Internal Processing Error"})
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# --- Routes ---

@router.post("/process-voice")
async def process_voice(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in SUPPORTED_AUDIO:
        raise HTTPException(status_code=400, detail=f"Unsupported audio format: {ext}")

    job_id = str(uuid.uuid4())
    update_job_status(job_id, "processing")
    
    tmp_path = await save_temp_file(file)
    background_tasks.add_task(
        run_pipeline_task, job_id, current_user['id'], tmp_path, process_voice_entry, "Voice"
    )

    return {"status": "accepted", "job_id": job_id}


@router.post("/process-ledger")
async def process_ledger(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in SUPPORTED_IMAGES:
        raise HTTPException(status_code=400, detail="Invalid image format")

    job_id = str(uuid.uuid4())
    update_job_status(job_id, "processing")

    tmp_path = await save_temp_file(file)
    background_tasks.add_task(
        run_pipeline_task, job_id, current_user['id'], tmp_path, process_ledger_image, "OCR"
    )

    return {"status": "accepted", "job_id": job_id}


@router.get("/status/{job_id}")
async def check_status(job_id: str):
    status = get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job ID not found")
    return status


@router.post("/confirm-transaction")
async def confirm_tx(
    data: VoiceTransaction, 
    current_user: dict = Depends(get_current_user),
    graph_service: GraphService = Depends(GraphService) # Using as a dependency
):
    if not graph_service.is_available():
        raise HTTPException(status_code=503, detail="Database connection unavailable")

    user_id = current_user['id']
    tx_data = data.model_dump()
    
    # Logic execution
    new_score = graph_service.log_transaction(user_id, tx_data)
    is_verified = graph_service.verify_transaction(user_id, tx_data['amount'])

    if is_verified:
        new_score = graph_service.recalculate_user_score(user_id)

    return {
        "status": "success", 
        "new_score": new_score, 
        "verified": bool(is_verified),
        "message": "Transaction verified and logged!" if is_verified else "Logged to ledger"
    }