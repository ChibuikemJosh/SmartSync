from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Any, Dict
import re

# --- Shared Utilities ---
def clean_numeric_string(v: str) -> str:
    """Helper to strip currency symbols and common separators."""
    if not isinstance(v, str): return str(v)
    return v.upper().replace("NGN", "").replace("NAIRA", "").replace("₦", "").replace(",", "").strip()

# --- Models ---

class VoiceTransaction(BaseModel):
    model_config = ConfigDict(from_attributes=True) # Allows Pydantic to read Neo4j dicts

    item: str = Field(..., description="The name of the item sold or expense incurred")
    amount: float = Field(..., gt=0, description="The cost in Naira (must be positive)")
    quantity: int = Field(default=1)
    unit: str = Field(default="item", description="The unit of the item (e.g., 'kg', 'piece')")
    type: str = Field(..., pattern="^(SALE|EXPENSE|CREDIT|DEBIT|GIG_COMPLETE|GIG_CONFIRMED)$")
    timestamp: Optional[str] = None
    notes: Optional[str] = "No additional notes"
    verified: bool = False
    is_anomaly: bool = False

    @field_validator('amount', mode='before')
    @classmethod
    def parse_amount(cls, v: Any) -> float:
        if isinstance(v, str):
            clean_v = clean_numeric_string(v)
            # Handle "5k" or "10K" shorthand
            if 'K' in clean_v:
                try:
                    # Remove 'K' and any non-numeric leftover, then multiply
                    num_part = re.sub(r'[^\d\.]', '', clean_v.split('K')[0])
                    return float(num_part) * 1000
                except (ValueError, IndexError):
                    return 0.0
            
            # Standard numeric cleanup
            clean_v = re.sub(r'[^\d\.]', '', clean_v)
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
            except (ValueError, TypeError, AttributeError):
                return 1
        return int(v) if v is not None else 1

# --- Communication Models ---

class ChatRequest(BaseModel):
    message: Optional[str] = None
    voice_path: Optional[str] = None

class VoiceProcessResponse(BaseModel):
    status: str
    transaction: Optional[VoiceTransaction] = None
    message: Optional[str] = None

class OCRProcessResponse(BaseModel):
    status: str
    extracted_data: Dict[str, Any]
    image_text: str

# --- User & Profile Models ---

class LocationSchema(BaseModel):
    city: str
    state: str
    country: str = "Nigeria"

class TierInfo(BaseModel):
    name: str = "Bronze"
    color: str = "#CD7F32"
    next_milestone: int = 100

class UserCreate(BaseModel):
    id: str
    name: str
    email: str
    password: str
    role: str = Field(..., pattern="^(Trader|Worker|Both)$")
    location: LocationSchema

class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    role: str
    location: LocationSchema
    trust_score: int = 43
    tier: TierInfo = Field(default_factory=TierInfo)
    skills: List[str] = []

class DashboardResponse(BaseModel):
    profile: UserProfile
    recent_transactions: List[VoiceTransaction]

# --- Squad/Financial Models ---

class VirtualAccountRequest(BaseModel):
    merchant_id: str
    business_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: str
    phone: str

    @field_validator('phone')
    @classmethod
    def validate_nigerian_phone(cls, v: str) -> str:
        # Standardizes: +234..., 080..., 070...
        clean_phone = re.sub(r'\s+|-', '', v)
        pattern = r'^(\+234|0)[789][01]\d{8}$'
        if not re.match(pattern, clean_phone):
            raise ValueError('Use a valid Nigerian phone number (e.g., 08012345678)')
        return clean_phone

class WithdrawalRequest(BaseModel):
    user_id: str
    amount: float = Field(..., gt=0)
    bank_code: str
    account_number: str = Field(..., min_length=10, max_length=10)
    narration: Optional[str] = "SmartSync withdrawal"


class PaymentLinkRequest(BaseModel):
    user_id: str
    amount: float = Field(..., gt=0)
    description: Optional[str] = "Payment for goods/services"

class EscrowRequest(BaseModel):
    buyer_id: str
    seller_id: str
    amount: float = Field(..., gt=0)
    description: Optional[str] = "Escrow for goods/services"