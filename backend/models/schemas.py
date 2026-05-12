"""
Pydantic models for validation and documentation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Any, Dict


class VoiceTransaction(BaseModel):
    item: str = Field(..., description="The name of the item sold or expense incurred")
    amount: int = Field(..., gt=0, description="The cost in Naira (must be positive)")
    quantity: int = Field(default=1)
    type: str = Field(..., pattern="^(SALE|EXPENSE)$")
    timestamp: Optional[str] = None
    notes: Optional[str] = "No additional notes"
    verified: bool = False # Default to False until verified by Squad

    @validator('amount', pre=True)
    def ensure_int(cls, v):
        # In case the AI sends "5000" instead of 5000
        if isinstance(v, str):
            # Strip NGN, commas, and handle 'k'
            clean_v = v.upper().replace("NGN", "").replace("NAIRA", "").replace(",", "").strip()
            if 'K' in clean_v:
                try:
                    result = int(float(clean_v.replace("K", "")) * 1000)
                    return result
                except ValueError:
                    pass
            return int(clean_v)
        return v
    
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


class UserProfile(BaseModel):
    id: str = Field(..., description="Unique ID")
    name: str
    role: str = Field(..., pattern="^(Trader|Worker|Both)$")
    location: LocationSchema
    trust_score: int = 43
    tier: TierInfo
    skills: Optional[list[str]] = []


class DashboardResponse(BaseModel):
    profile: UserProfile
    recent_transactions: list[VoiceTransaction]


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    code: Optional[int] = None
    details: Optional[Any] = None