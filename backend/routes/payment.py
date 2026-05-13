from fastapi import APIRouter, Request, Header, HTTPException
from services.database import GraphService
import logging

router = APIRouter()
db = GraphService()

@router.post("/squad-webhook")
async def handle_squad_webhook(request: Request):
    """
    This is the URL you give to Squad in their dashboard.
    """
    # 1. Get the data from Squad
    payload = await request.json()
    
    # Squad usually sends 'body' containing transaction details
    data = payload.get("body", {})
    transaction_ref = data.get("transaction_ref")
    amount = data.get("amount") # Amount in Kobo or Naira depending on config
    # For many Nigerian APIs, you might need to convert Kobo to Naira
    actual_amount = amount / 100 if amount >= 100 else amount 
    
    # We use a unique ID like the virtual account number or email to find the user
    # For now, let's assume Squad sends a metadata field with our internal user_id
    user_id = data.get("meta", {}).get("user_id")

    if not user_id:
        return {"status": "ignored", "message": "No internal user_id found"}

    # 2. MATCHING LOGIC
    # We call your verify_transaction method to find the matching Voice Log
    verified_item = db.verify_transaction(user_id, actual_amount)

    if verified_item:
        # 3. If matched, recalculate the score (they get the verification boost!)
        history = db._get_user_history(user_id)
        new_score = db.calculate_decayed_score(history)
        db._update_user_score(user_id, new_score)
        
        return {"status": "success", "verified": True, "item": verified_item, "message": "Transaction verified and score updated", "new_score": new_score}

    # If no match found yet, we should still log the payment to Neo4j 
    # so it can be matched later if the user records the voice note late.
    return {"status": "logged", "verified": False, "message": "Transaction logged but not verified yet. Will be matched against future voice logs.", "new_score": new_score}