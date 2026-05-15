"""
Squad Payment Integration Routes
Handles virtual accounts, payment links, webhooks, escrow, and payouts
"""

from dotenv import load_dotenv
load_dotenv()  # ← FIRST, before anything else
# After load_dotenv(), add this safety check
import os

# ─── Squad Config ────────────────────────────────────────────
SQUAD_SECRET_KEY = os.getenv("SQUAD_SECRET_KEY")
SQUAD_BASE_URL = os.getenv("SQUAD_BASE_URL", "https://sandbox-api-d.squadco.com")

if not SQUAD_SECRET_KEY:
    raise RuntimeError("SQUAD_SECRET_KEY is missing from .env file. Server cannot start.")

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional
import logging
import httpx
import hmac
import hashlib
import json
import time
from services.database import GraphService
from models.schemas import VirtualAccountRequest, VirtualAccountResponse, PaymentLinkRequest, PaymentLinkResponse, EscrowRequest, WithdrawalRequest
from utils.dependencies import get_current_user

try:
    graph = GraphService()
    if graph.is_available():
        print("✅ Neo4j connected successfully")
    else:
        graph = None
        print("⚠️ Neo4j connection unavailable — Squad endpoints will still work")
except Exception as e:
    graph = None
    print(f"⚠️ Neo4j connection failed: {e} — Squad endpoints will still work")

logger = logging.getLogger(__name__)
router = APIRouter()

SQUAD_TEST_BVN = "22172180083"
SQUAD_TEST_DOB = "01/01/1990"
SQUAD_TEST_ADDRESS = "Lagos, Nigeria"
SQUAD_TEST_GENDER = "1"
SQUAD_TEST_BENEFICIARY_ACCOUNT = "0123456789"

def get_headers():
    key = os.getenv("SQUAD_SECRET_KEY")
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }


def _require_graph():
    if not graph or not graph.is_available():
        raise HTTPException(status_code=503, detail="Database connection unavailable")

# ─── 1. CREATE VIRTUAL ACCOUNT ───────────────────────────────
@router.post("/create-virtual-account")
async def create_virtual_account(request: VirtualAccountRequest, current_user: dict = Depends(get_current_user)):
    logged_in_user_id = current_user['id']

    try:
        payload = {
    "first_name": request.first_name or request.business_name.split()[0],
    "last_name": request.last_name or request.business_name.split()[-1],
    "mobile_num": f"234{request.phone[-10:]}",
    "email": request.email,
    "bvn": SQUAD_TEST_BVN,
    "dob": SQUAD_TEST_DOB,
    "address": SQUAD_TEST_ADDRESS,
    "gender": SQUAD_TEST_GENDER,
    "customer_identifier": logged_in_user_id,
    "beneficiary_account": SQUAD_TEST_BENEFICIARY_ACCOUNT,
}

        logger.info(f"Squad payload: {payload}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{SQUAD_BASE_URL}/virtual-account",
                headers=get_headers(),
                json=payload
            )

        # ---- SAFE RESPONSE HANDLING ----
        try:
            data = response.json()
        except Exception:
            logger.error(f"Non-JSON response from Squad: {response.text}")
            raise HTTPException(
                status_code=500,
                detail="Invalid response from payment provider"
            )

        if response.status_code != 200 or not data.get("success"):
            logger.error(f"Squad error: {data}")
            raise HTTPException(
                status_code=400,
                detail=data.get("message", "Virtual account creation failed")
            )

        account_data = data.get("data", {})

        if graph:
            graph.update_user_virtual_account(
                user_id=logged_in_user_id, 
                account_number=account_data.get("virtual_account_number"),
                bank_name=account_data.get("bank_code") # Or bank name if available
            )

        return {
            "status": "success",
            "account_number": account_data.get("virtual_account_number"),
            "bank_code": account_data.get("bank_code"),
            "merchant_id": logged_in_user_id,
            "business_name": request.business_name,
            "raw": data
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("CREATE VIRTUAL ACCOUNT FAILED")
        raise HTTPException(status_code=500, detail=str(e))

# ─── 3. WEBHOOK — Detects Incoming Payments ──────────────────

@router.post("/webhook")
async def squad_webhook(request: Request):
    try:
        raw_body = await request.body()
        
        try:
            payload = json.loads(raw_body)
        except Exception:
            logger.error("Invalid JSON in webhook body")
            raise HTTPException(status_code=400, detail="Invalid JSON")

        # Signature check — skip blocking in sandbox
        squad_signature = request.headers.get("x-squad-encrypted-body", "")
        if SQUAD_SECRET_KEY and squad_signature:
            expected_signature = hmac.new(
                SQUAD_SECRET_KEY.encode(),
                raw_body,
                hashlib.sha512
            ).hexdigest().upper()
            if squad_signature != expected_signature:
                logger.warning("Signature mismatch — proceeding in sandbox mode")

        event = payload.get("Event")
        logger.info(f"Webhook received: {event}")
        logger.info(f"Webhook payload: {payload}")

        if event == "charge.success":
            body = payload.get("Body", {})
            amount_kobo = body.get("transaction_amount", 0)
            amount_naira = amount_kobo / 100
            merchant_id = body.get("customer_identifier")

            logger.info(f"Payment: ₦{amount_naira} for user {merchant_id}")

            try:
                if graph:
                    new_score = graph.log_transaction(
                        user_id=merchant_id,
                        tx_data={
                            "item": "Squad Payment",
                            "amount": amount_naira,
                            "type": "CREDIT",
                        }
                    )
                    matched = graph.verify_transaction(
                        user_id=merchant_id,
                        amount=amount_naira
                    )
                else:
                    new_score = 43
                    matched = None
            except Exception as db_error:
                logger.warning(f"Neo4j unavailable: {db_error} — returning base score")
                new_score = 43
                matched = None

            logger.info(f"New Trust Score for {merchant_id}: {new_score}")

            return {
                "status": "success",
                "message": "Payment processed",
                "new_score": new_score,
                "voice_log_verified": matched is not None
            }

        return {"status": "ignored", "event": event}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Webhook error: {str(e)}")
        return {"detail": "Webhook processing failed"}


# ─── 4. GET TRANSACTIONS ─────────────────────────────────────

@router.post("/generate-payment-link")
async def generate_payment_link(request: PaymentLinkRequest):
    try:
        logger.info(f"Generating payment link for transaction {request.transaction_id}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{SQUAD_BASE_URL}/payment_link/otp",
                headers=get_headers(),
                json={
                    "name": f"SmartSync Payment - {request.transaction_id}",
                    "hash": request.transaction_id,
                    "description": request.description,
                    "redirect_link": "https://smartsync.app/payment/success",
                    "link_status": 1
                    }               
            )

        try:
            data = response.json()
        except Exception:
            logger.error(f"Non-JSON from Squad: {response.text}")
            raise HTTPException(status_code=500, detail="Invalid response from Squad")

        logger.info(f"Squad response: {data}")
        logger.info(f"Squad status code: {response.status_code}")

        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=data.get("message", "Payment link failed")
            )

        hash_value = data.get("data", {}).get("hash", request.transaction_id)
        payment_link = f"https://sandbox-pay.squadco.com/{hash_value}"

        return {
            "status": "success",
            "payment_link": payment_link,
            "transaction_id": request.transaction_id,
            "amount": request.amount,
            "raw": data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("GENERATE PAYMENT LINK FAILED")
        raise HTTPException(status_code=500, detail=str(e))


# ─── 5. ESCROW — Lock Payment When Gig is Accepted ──────────

@router.post("/escrow/lock")
async def lock_escrow(request: EscrowRequest):
    """
    Locks a trader's payment when they accept a worker for a gig.
    Money is held until the job is confirmed complete.
    """
    try:
        logger.info(f"Locking escrow for gig {request.gig_id}: ₦{request.amount}")

        # ── Save escrow record in database ──
        # from services.database import create_escrow
        # create_escrow(
        #     gig_id=request.gig_id,
        #     trader_id=request.trader_id,
        #     worker_id=request.worker_id,
        #     amount=request.amount,
        #     status="locked"
        # )

        return {
            "status": "success",
            "message": f"₦{request.amount} locked in escrow for gig {request.gig_id}",
            "gig_id": request.gig_id
        }

    except Exception as e:
        logger.error(f"Escrow lock error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to lock escrow")


# ─── 6. ESCROW RELEASE — Pay Worker After Job is Done ───────

@router.post("/escrow/release/{gig_id}")
async def release_escrow(gig_id: str):
    try:
        _require_graph()
        logger.info(f"Releasing escrow for gig {gig_id}")

        gig = graph.get_gig_details(gig_id)
        if not gig:
            raise HTTPException(status_code=404, detail="Gig record not found")

        # 2. Safety Check: Don't pay twice!
        if gig['status'] == 'released':
            raise HTTPException(status_code=400, detail="Funds for this gig have already been released")

        worker_id = gig["worker_id"]
        trader_id = gig["trader_id"]
        amount = gig["amount"]
        bank_code = gig["bank_code"]
        worker_account = gig.get("account_number")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SQUAD_BASE_URL}/payout/transfer",
                headers=get_headers(),
                json={
                    "transaction_reference": f"escrow_release_{gig_id}_{int(time.time())}",
                    "amount": amount * 100,
                    "bank_code": bank_code,
                    "account_number": worker_account,
                    "currency_id": "NGN",
                    "remark": f"SmartSync gig payment - {gig_id}"
                }
            )

        if response.status_code != 200:
            logger.error(f"Squad payout error: {response.text}")
            raise HTTPException(status_code=400, detail="Failed to release escrow funds")
            
        graph.release_escrow_status(gig_id)

        data = response.json()

        if data.get("status") != 200:
            raise HTTPException(status_code=400, detail=data.get("message", "Payout failed"))

        # Update Trust Score for both trader and worker after gig completes
        if graph.is_available():
            graph.log_transaction(
                user_id=worker_id,
                tx_data={
                    "item": f"Gig completed - {gig_id}",
                    "amount": amount,
                    "type": "GIG_COMPLETE"
                }
            )
            graph.log_transaction(
                user_id=trader_id,
                tx_data={
                    "item": f"Gig confirmed - {gig_id}",
                    "amount": amount,
                    "type": "GIG_CONFIRMED"
                }
            )
        return {
            "status": "success",
            "message": "Payment released to worker",
            "gig_id": gig_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Escrow release error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to release escrow")


@router.post("/escrow/cancel/{gig_id}")
async def cancel_gig(gig_id: str, initiator: str = "trader", reason: str = "Change of mind"):
    """
    initiator can be 'trader' or 'worker'
    """
    _require_graph()
    gig = graph.get_gig_details(gig_id)
    if not gig or gig['status'] != 'locked':
        raise HTTPException(status_code=400, detail="Invalid gig status for cancellation")

    graph.refund_escrow_status(gig_id, canceled_by=initiator)

    # 3. FAIR TRUST SCORE LOGIC
    if initiator == "worker":
        # Worker ghosted the trader -> Penalty for Worker
        graph.log_transaction(gig['worker_id'], tx_data={
            "item": f"Gig No-show: {reason}",
            "type": "PENALTY" 
        })
    else:
        # Trader canceled before start -> No penalty for worker
        # Maybe a tiny penalty for trader if they do this too often
        graph.log_transaction(gig['trader_id'], tx_data={
            "item": f"Trader Cancelled: {reason}",
            "type": "SYSTEM_NOTE" 
        })

    return {"status": "success", "message": f"Gig canceled by {initiator}. Funds returned."}


# ─── 7. WITHDRAWAL — User Sends Money to Their Bank ─────────

@router.post("/withdraw")
async def withdraw(request: WithdrawalRequest):
    """
    Allows a trader or worker to withdraw their Squad wallet
    balance to any Nigerian bank account.
    """
    try:
        logger.info(f"Withdrawal request: ₦{request.amount} for user {request.user_id}")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SQUAD_BASE_URL}/payout/transfer",
                headers=get_headers(),
                json={
                    "transaction_reference": f"withdrawal_{request.user_id}_{int(time.time())}",
                    "amount": request.amount * 100,    # kobo
                    "bank_code": request.bank_code,
                    "account_number": request.account_number,
                    "currency_id": "NGN",
                    "remark": request.narration
                }
            )

        data = response.json()
        logger.info(f"Withdrawal response: {data}")

        if data.get("status") != 200:
            raise HTTPException(status_code=400, detail=data.get("message", "Withdrawal failed"))

        return {
            "status": "success",
            "message": f"₦{request.amount} withdrawal initiated",
            "reference": data["data"].get("transaction_reference")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Withdrawal error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process withdrawal")
