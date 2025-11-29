"""
Pydantic models for request/response validation and serialization.
These models define the API contract and ensure type safety.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List

class CartItem(BaseModel):
    """Represents an item in the shopping cart."""

    product_id: int = Field(..., gt=0, description="Unique product identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    price: float = Field(..., gt=0, description="Product price")
    quantity: int = Field(..., gt=0, description="Quantity of items")

    @field_validator('price')
    @classmethod
    def validate_price(cls, v: float) -> float:
        """Ensure price has maximum 2 decimal places."""
        return round(v, 2)


class CartResponse(BaseModel):
    """Response model for cart operations."""
    
    items: List[CartItem] = Field(default_factory=list)
    total_items: int = Field(..., ge=0)
    subtotal: float = Field(..., ge=0)
