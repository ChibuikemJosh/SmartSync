from fastapi import APIRouter

from models.squad import PaymentLinkRequest, VirtualAccountRequest
from services.squad_service import create_virtual_account, generate_payment_link

router = APIRouter(prefix="/squad", tags=["squad"])


@router.post("/virtual-account")
def create_virtual_account_endpoint(payload: VirtualAccountRequest) -> dict:
    return create_virtual_account(payload.model_dump(exclude_none=True))


@router.post("/payment-link")
def generate_payment_link_endpoint(payload: PaymentLinkRequest) -> dict:
    return generate_payment_link(payload.model_dump(exclude_none=True))
