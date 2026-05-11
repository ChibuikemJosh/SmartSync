"""
Pydantic models for validation and documentation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional

class VoiceTransaction(BaseModel):
    item: str = Field(..., description="The name of the item sold or expense incurred")
    amount: int = Field(..., gt=0, description="The cost in Naira (must be positive)")
    quantity: int = Field(default=1)
    type: str = Field(..., pattern="^(SALE|EXPENSE)$")
    notes: Optional[str] = "No additional notes"

    @validator('amount', pre=True)
    def ensure_int(cls, v):
        # In case the AI sends "5000" instead of 5000
        if isinstance(v, str):
            return int(v.replace(",", "").replace("k", "000"))
        return v