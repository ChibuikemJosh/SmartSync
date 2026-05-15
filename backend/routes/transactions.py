import logging
from fastapi import APIRouter, HTTPException, Depends, status
from models.schemas import VoiceTransaction
from services.database import GraphService
from utils.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)
db = GraphService()

@router.put("/update/{tx_id}")
async def update_transaction(
    tx_id: str, 
    new_data: VoiceTransaction, 
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user['id']

    # 1. Ownership & Existence Check
    # We must ensure this transaction belongs to the person trying to edit it
    tx_details = db.get_transaction_by_id(tx_id)
    
    if not tx_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Oga, we no fit find this transaction record."
        )

    # Security check: Does this tx belong to the current user?
    if tx_details.get('user_id') != user_id:
        logger.warning(f"Unauthorized update attempt by User {user_id} on Tx {tx_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You no get permission to touch this record!"
        )

    # 2. Verification Check
    # If it's already verified, it's locked for integrity (Trust Score protection)
    if tx_details.get('verified'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="This transaction don already verified. You no fit edit am again."
        )

    # 3. Proceed with Update
    try:
        # We use exclude_unset=True so we don't overwrite existing data with Nones
        update_payload = new_data.model_dump(exclude_unset=True)
        
        db.update_transaction_node(tx_id, update_payload)
        
        # Recalculate the trust score since the transaction data (amount/type) changed
        new_score = db.recalculate_user_score(user_id)
        
        return {
            "status": "success",
            "message": "Transaction updated sharp-sharp!",
            "new_score": new_score,
            "updated_fields": list(update_payload.keys())
        }
        
    except Exception as e:
        logger.error(f"Update failed for Tx {tx_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Something go wrong for our side, try again small time."
        )