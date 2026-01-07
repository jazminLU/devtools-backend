from pydantic import BaseModel, Field
from typing import Dict, List


class ShoppingTotalRequest(BaseModel):
    costs: Dict[str, float] = Field(..., description="Dictionary mapping item names to their costs")
    items: List[str] = Field(..., description="List of items to calculate total for")
    tax: float = Field(..., ge=0, description="Tax rate as a decimal (e.g., 0.1 for 10%)")


class ShoppingTotalResponse(BaseModel):
    subtotal: float
    tax_amount: float
    total: float
    items_found: List[str]
    items_not_found: List[str]

