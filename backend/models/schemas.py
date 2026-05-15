from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any, Dict
import re

# --- Shared Utilities ---
def clean_numeric_string(v: str) -> str:
    """Helper to strip currency symbols and common separators."""
    return v.upper().replace("NGN", "").replace("NAIRA", "").replace(",", "").strip()

# --- Models ---

class VoiceTransaction(BaseModel):
    item: str = Field(..., description="The name of the item sold or expense incurred")
    amount: float = Field(..., gt=0, description="The cost in Naira (must be positive)")
    quantity: int = Field(default=1)
    unit: str = Field(default="item", description="The unit of the item (e.g., 'kg', 'piece')")
    type: str = Field(..., pattern="^(SALE|EXPENSE|CREDIT|DEBIT|GIG_COMPLETE|GIG_CONFIRMED)$")
    timestamp: str | None = None
    notes: str | None = "No additional notes"
    verified: bool = False
    is_anomaly: bool = False

    @field_validator('amount', mode='before')
    @classmethod
    def parse_amount(cls, v: Any) -> float:
        if isinstance(v, str):
            clean_v = clean_numeric_string(v)
            clean_v = re.sub(r'[^\d\.K]', '', clean_v)
            if 'K' in clean_v:
                try:
                    return float(clean_v.replace("K", "")) * 1000
                except ValueError:
                    return 0.0
            try:
                return float(clean_v)
            except ValueError:
                return 0.0
        return float(v) if v is not None else 0.0

    @field_validator('quantity', mode='before')
    @classmethod
    def parse_quantity(cls, v: Any) -> int:
        if isinstance(v, str):
            try:
                # Extracts the first number found in a string like "5 bags"
                match = re.search(r"[-+]?\d*\.\d+|\d+", v)
                return int(float(match.group())) if match else 1
            except (ValueError, TypeError):
                return 1
        return int(v) if v is not None else 1


class ChatRequest(BaseModel):
    """New model for handling combined text and voice inputs."""
    message: str | None = None
    voice_path: str | None = None


class VoiceProcessResponse(BaseModel):
    status: str
    transaction: VoiceTransaction | None = None
    message: str | None = None


class OCRProcessResponse(BaseModel):
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
    email: str
    password: str
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
    skills: List[str] = []


class DashboardResponse(BaseModel):
    profile: UserProfile
    recent_transactions: List[VoiceTransaction]


# --- Squad/Financial Models ---

class VirtualAccountRequest(BaseModel):
    merchant_id: str
    business_name: str
    first_name: str | None = None
    last_name: str | None = None
    email: str
    phone: str

    @field_validator('phone')
    @classmethod
    def validate_nigerian_phone(cls, v: str) -> str:
        pattern = r'^(\+234|0)[789][01]\d{8}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid Nigerian phone number format')
        return v.strip()


class PaymentLinkRequest(BaseModel):
    merchant_id: str
    amount: float
    transaction_id: str
    description: str
    customer_email: str | None = None


class WithdrawalRequest(BaseModel):
    user_id: str
    amount: float
    bank_code: str
    account_number: str
    narration: str | None = "SmartSync withdrawal"

class EscrowRequest(BaseModel):
    user_id: str
    amount: float
    description: str