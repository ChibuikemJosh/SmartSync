"""
Pydantic models for validation and documentation
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Any, Dict
import re


class VoiceTransaction(BaseModel):
    item: str = Field(..., description="The name of the item sold or expense incurred")
    amount: float = Field(..., gt=0, description="The cost in Naira (must be positive)")
    quantity: int = Field(default=1)
    unit: str = Field(default="item", description="The unit of the item (e.g., 'kg', 'piece', bag, derica, paint, kg)")
    type: str = Field(..., pattern="^(SALE|EXPENSE|CREDIT|DEBIT|GIG_COMPLETE|GIG_CONFIRMED)$")
    timestamp: Optional[str] = None
    notes: Optional[str] = "No additional notes"
    verified: bool = False # Default to False until verified by Squad
    is_anomaly: bool = False # Flag for potential fraud or errors, set by backend logic

    @validator('amount', pre=True)
    def ensure_float_amount(cls, v):
        # In case the AI sends "5000" instead of 5000
        if isinstance(v, str):
            # Strip NGN, commas, and handle 'k'
            clean_v = v.upper().replace("NGN", "").replace("NAIRA", "").replace(",", "").strip()
            clean_v = re.sub(r'[^\d\.Kk]', '', clean_v) # Remove any non-numeric, non-dot, non-K characters
            if 'K' in clean_v:
                try:
                    result = float(clean_v.replace("K", "")) * 1000
                    return result
                except ValueError:
                    return 0.0 # Default to 0.0 if we can't parse it

            try:
                return float(clean_v)
            except ValueError:
                return float(v) if v else 0.0

        try:
            return float(v)
        except (TypeError, ValueError):
            return 0.0
            
    @validator('quantity', pre=True)
    def ensure_int_quantity(cls, v):
        """Ensures quantity is a clean integer, even if AI sends strings or floats."""
        if isinstance(v, str):
            try:
                # Handle common textual numbers (Optional: add a dict for 'one','two', etc. if needed)
                clean_v = v.strip().split()[0] # Take first part in case of "5 units"
                return int(float(clean_v))
            except (ValueError, TypeError):
                return 1 # Default to 1 if we can't parse it
        if isinstance(v, float):
            return int(v)
        return v
    

class VoiceProcessResponse(BaseModel):
    status: str
    transaction: Optional[VoiceTransaction] = None
    message: Optional[str] = None

class OCRProcessResponse(BaseModel):
    """Response model for OCR processing"""
    status: str
    extracted_data: Dict[str, Any]
    image_text: str

class LocationSchema(BaseModel):
    city: str
    state: str
    country: str


class TierInfo(BaseModel):
    name: str
    color: str
    next_milestone: int


class UserCreate(BaseModel):
    id: str
    name: str
    email: str # Added email
    password: str # Added password
    role: str = Field(..., pattern="^(Trader|Worker|Both)$")
    location: LocationSchema


class UserProfile(BaseModel):
    id: str = Field(..., description="Unique ID")
    name: str
    email: str
    role: str = Field(..., pattern="^(Trader|Worker|Both)$")
    location: LocationSchema
    trust_score: int = 43
    tier: TierInfo
    skills: Optional[list[str]] = []


class DashboardResponse(BaseModel):
    profile: UserProfile
    recent_transactions: list[VoiceTransaction]


# Response and Request models for Squad routes

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    code: Optional[int] = None
    details: Optional[Any] = None


class VirtualAccountRequest(BaseModel):
    merchant_id: str
    business_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: str
    phone: str

    @validator('phone')
    def validate_nigerian_phone(cls, v):
        # Basic regex for Nigerian phone numbers (starts with +234 or 0, followed by 10 digits)
        pattern = r'^(\+234|0)[789][01]\d{8}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid Nigerian phone number format')
        return v.strip()


class VirtualAccountResponse(BaseModel):
    status: str
    account_number: str
    bank_name: str
    merchant_id: str
    business_name: str


class PaymentLinkRequest(BaseModel):
    merchant_id: str
    amount: float
    transaction_id: str
    description: str
    customer_email: Optional[str] = None


class PaymentLinkResponse(BaseModel):
    status: str
    payment_link: str
    transaction_id: str
    amount: float


class EscrowRequest(BaseModel):
    gig_id: str
    trader_id: str
    worker_id: str
    amount: float


class WithdrawalRequest(BaseModel):
    user_id: str
    amount: float          # in Naira
    bank_code: str
    account_number: str
    narration: Optional[str] = "SmartSync withdrawal"