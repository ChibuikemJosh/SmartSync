from fastapi import APIRouter, HTTPException
from models.schemas import VoiceTransaction
from services.database import GraphService

router = APIRouter()
db = GraphService()

@router.put("/update/{tx_id}")
async def update_transaction(tx_id: str, new_data: VoiceTransaction):
    # 1. Check if verified first
    is_verified = db.check_if_verified(tx_id) 
    if is_verified:
        raise HTTPException(status_code=403, detail="Cannot edit verified transactions!")
    
    # 2. Proceed with update
    db.update_transaction_node(tx_id, new_data.model_dump())
    return {"status": "success"}