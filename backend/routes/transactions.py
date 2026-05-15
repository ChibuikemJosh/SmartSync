from fastapi import APIRouter, HTTPException, Depends
from models.schemas import VoiceTransaction
from services.database import GraphService
from utils.dependencies import get_current_user

router = APIRouter()
db = GraphService()

@router.put("/update/{tx_id}")
async def update_transaction(tx_id: str, new_data: VoiceTransaction, current_user: dict = Depends(get_current_user)):
    # 1. Check if verified first
    is_verified = db.check_if_verified(tx_id)
    if is_verified:
        raise HTTPException(status_code=403, detail="Cannot edit verified transactions!")

    # 2. Proceed with update
    try:
        db.update_transaction_node(tx_id, new_data.model_dump())
        new_score = db.recalculate_user_score(current_user['id'])
        return {
            "status": "success",
            "message": "Transaction updated successfully",
            "new_score": new_score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")