"""
Squad Payment Integration Routes
Handles virtual accounts, payment links, webhooks, escrow, and payouts
"""
import os
import logging
import httpx
import hmac
import hashlib
import json
import time
from typing import Optional
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request, Depends, status

# Load environment before other imports
load_dotenv()

from services.database import GraphService
from models.schemas import (
    VirtualAccountRequest, 
    PaymentLinkRequest, 
    EscrowRequest, 
    WithdrawalRequest
)
from utils.dependencies import get_current_user

# --- Configuration ---
SQUAD_SECRET_KEY = os.getenv("SQUAD_SECRET_KEY")
SQUAD_BASE_URL = os.getenv("SQUAD_BASE_URL", "https://sandbox-api-d.squadco.com")

if not SQUAD_SECRET_KEY:
    raise RuntimeError("SQUAD_SECRET_KEY is missing. Payment services unavailable.")

router = APIRouter()
logger = logging.getLogger(__name__)

# Sandbox Test Constants
SQUAD_TEST_BVN = "22172180083"
SQUAD_TEST_DOB = "01/01/1990"
SQUAD_TEST_ADDRESS = "Lagos, Nigeria"
SQUAD_TEST_GENDER = "1"
SQUAD_TEST_BENEFICIARY_ACCOUNT = "0123456789"

# Database Initialization
try:
    graph = GraphService()
except Exception as e:
    logger.error(f"Neo4j Initialization Failed: {e}")
    graph = None

def get_headers():
    return {
        "Authorization": f"Bearer {SQUAD_SECRET_KEY}",
        "Content-Type": "application/json"
    }

# --- 1. CREATE VIRTUAL ACCOUNT ---
@router.post("/create-virtual-account")
async def create_virtual_account(
    request: VirtualAccountRequest, 
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user['id']
    
    # Handle name splitting safely
    names = request.business_name.split()
    f_name = request.first_name or names[0]
    l_name = request.last_name or (names[-1] if len(names) > 1 else "Merchant")

    payload = {
        "first_name": f_name,
        "last_name": l_name,
        "mobile_num": f"234{request.phone[-10:]}",
        "email": request.email,
        "bvn": SQUAD_TEST_BVN,
        "dob": SQUAD_TEST_DOB,
        "address": SQUAD_TEST_ADDRESS,
        "gender": SQUAD_TEST_GENDER,
        "customer_identifier": user_id,
        "beneficiary_account": SQUAD_TEST_BENEFICIARY_ACCOUNT,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{SQUAD_BASE_URL}/virtual-account",
                headers=get_headers(),
                json=payload
            )
            data = response.json()
            
            if response.status_code != 200 or not data.get("success"):
                logger.error(f"Squad VA Error: {data}")
                raise HTTPException(status_code=400, detail=data.get("message", "Account creation failed"))

            account_info = data.get("data", {})
            
            # Persist to Database if available
            if graph and graph.is_available():
                graph.update_user_virtual_account(
                    user_id=user_id,
                    account_number=account_info.get("virtual_account_number"),
                    bank_name=account_info.get("bank_name", "GTBank/Squad")
                )

            return {
                "status": "success",
                "account_number": account_info.get("virtual_account_number"),
                "bank_name": account_info.get("bank_name"),
                "merchant_id": user_id
            }

        except Exception as e:
            logger.exception("Virtual Account flow failed")
            raise HTTPException(status_code=500, detail=str(e))

# --- 2. WEBHOOK ---
@router.post("/webhook")
async def squad_webhook(request: Request):
    raw_body = await request.body()
    signature = request.headers.get("x-squad-encrypted-body")

    # Verify Signature
    if SQUAD_SECRET_KEY:
        computed_sig = hmac.new(
            SQUAD_SECRET_KEY.encode(),
            raw_body,
            hashlib.sha512
        ).hexdigest().upper()
        
        if signature != computed_sig:
            logger.warning("Webhook signature mismatch!")
            # In production, you might want to return 401 here.

    try:
        payload = json.loads(raw_body)
        event = payload.get("Event")
        
        if event == "charge.success":
            body = payload.get("Body", {})
            amount_naira = body.get("transaction_amount", 0) / 100
            user_id = body.get("customer_identifier")

            logger.info(f"Payment success: ₦{amount_naira} for User {user_id}")

            if graph and graph.is_available():
                graph.log_transaction(
                    user_id=user_id,
                    tx_data={"item": "Squad Inbound", "amount": amount_naira, "type": "CREDIT"}
                )
                graph.verify_transaction(user_id=user_id, amount=amount_naira)

            return {"status": "success"}

    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
    
    return {"status": "received"}

# --- 3. PAYMENT LINK ---
@router.post("/generate-payment-link")
async def generate_payment_link(request: PaymentLinkRequest):
    """Uses Squad Initiate to get a checkout URL"""
    payload = {
        "amount": int(request.amount * 100), # Convert to Kobo
        "email": request.email,
        "currency": "NGN",
        "initiate_type": "inline",
        "transaction_ref": f"link_{int(time.time())}_{request.transaction_id}",
        "callback_url": "https://smartsync.app/payment/success",
        "metadata": {"transaction_id": request.transaction_id}
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SQUAD_BASE_URL}/transaction/initiate",
            headers=get_headers(),
            json=payload
        )
        data = response.json()
        
        if data.get("status") != 200:
            raise HTTPException(status_code=400, detail=data.get("message"))
            
        return {
            "status": "success",
            "checkout_url": data["data"].get("checkout_url"),
            "transaction_ref": payload["transaction_ref"]
        }

# --- 4. ESCROW RELEASE ---
@router.post("/escrow/release/{gig_id}")
async def release_escrow(gig_id: str):
    if not graph:
        raise HTTPException(status_code=503, detail="Database connection missing")
        
    gig = graph.get_gig_details(gig_id)
    if not gig or gig.get('status') == 'released':
        raise HTTPException(status_code=400, detail="Invalid gig or already paid")

    # Transfer funds to worker
    payload = {
        "transaction_reference": f"rel_{gig_id}_{int(time.time())}",
        "amount": int(gig["amount"] * 100),
        "bank_code": gig["bank_code"],
        "account_number": gig["account_number"],
        "currency_id": "NGN",
        "remark": f"Release for Gig {gig_id}"
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(f"{SQUAD_BASE_URL}/payout/transfer", headers=get_headers(), json=payload)
        data = res.json()

        if data.get("status") != 200:
            logger.error(f"Payout Failed: {data}")
            raise HTTPException(status_code=400, detail="Payout failed at Squad")

        graph.release_escrow_status(gig_id)
        return {"status": "success", "message": "Funds released"}

# --- 5. WITHDRAWAL ---
@router.post("/withdraw")
async def withdraw(request: WithdrawalRequest):
    payload = {
        "transaction_reference": f"wd_{request.user_id}_{int(time.time())}",
        "amount": int(request.amount * 100),
        "bank_code": request.bank_code,
        "account_number": request.account_number,
        "currency_id": "NGN",
        "remark": request.narration or "Withdrawal"
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(f"{SQUAD_BASE_URL}/payout/transfer", headers=get_headers(), json=payload)
        data = res.json()

        if data.get("status") != 200:
            raise HTTPException(status_code=400, detail=data.get("message"))

        return {"status": "success", "reference": payload["transaction_reference"]}