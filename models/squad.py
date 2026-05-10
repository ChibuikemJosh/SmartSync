from decimal import Decimal

from pydantic import BaseModel


class VirtualAccountRequest(BaseModel):
    customer_name: str
    customer_email: str
    phone_number: str | None = None
    bvn: str | None = None


class PaymentLinkRequest(BaseModel):
    amount: Decimal
    currency: str = "NGN"
    description: str | None = None
