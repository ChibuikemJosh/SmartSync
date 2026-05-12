"""
Pydantic models for validation and documentation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Any


class VoiceTransaction(BaseModel):
    item: str = Field(..., description="The name of the item sold or expense incurred")
    amount: int = Field(..., gt=0, description="The cost in Naira (must be positive)")
    quantity: int = Field(default=1)
    type: str = Field(..., pattern="^(SALE|EXPENSE)$")
    notes: Optional[str] = "No additional notes"
    verified: bool = False # Default to False until verified by Squad

    @validator('amount', pre=True)
    def ensure_int(cls, v):
        # In case the AI sends "5000" instead of 5000
        if isinstance(v, str):
            # Strip NGN, commas, and handle 'k'
            clean_v = v.upper().replace("NGN", "").replace("NAIRA", "").replace(",", "").strip()
            if 'K' in clean_v:
                return int(float(clean_v.replace("K", "")) * 1000)
            return int(clean_v)
        return v


class LocationSchema(BaseModel):
    city: str
    state: str
    country: str


class UserProfile(BaseModel):
    id: str = Field(..., description="Unique ID")
    name: str
    role: str = Field(..., pattern="^(Trader|Worker|Both)$")
    location: LocationSchema
    trust_score: int = 43
    tier_name: str = "New"
    skills: Optional[list[str]] = []


class DashboardData(BaseModel):
    profile: UserProfile
    recent_activity: List[VoiceTransaction]


class TierInfo(BaseModel):
    name: str
    color: str
    next_milestone: int


class DashboardResponse(BaseModel):
    name: str
    trust_score: int
    tier: TierInfo
    recent_transactions: list[VoiceTransaction]


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    code: Optional[int] = None
    details: Optional[Any] = None