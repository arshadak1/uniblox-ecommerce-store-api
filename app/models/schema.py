"""
Pydantic models for request/response validation and serialization.
These models define the API contract and ensure type safety.
"""
import uuid

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


class User(BaseModel):
    session_id: str
    date_created: Optional[datetime]


# Cart Related Models
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


class AddToCartRequest(BaseModel):
    """Request model for adding items to cart."""

    product_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=200)
    price: float = Field(..., gt=0)
    quantity: int = Field(default=1, gt=0)


class UpdateCartRequest(BaseModel):
    """Request model for updating cart item quantity."""

    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


# Checkout Related Models
class CheckoutRequest(BaseModel):
    """Request model for checkout."""
    discount_code: Optional[str] | None = Field(None, max_length=50)

    @field_validator('discount_code')
    @classmethod
    def validate_discount_code(cls, v: Optional[str]) -> Optional[str]:
        """Normalize discount code to uppercase."""
        return v.upper() if v else None


class CheckoutResponse(BaseModel):
    """Response model for successful checkout."""

    order_id: str
    subtotal: float
    discount_applied: bool
    discount_amount: float = 0.0
    total_amount: float
    new_discount_code: Optional[str] = None
    message: str
    timestamp: datetime


class Order(BaseModel):
    order_id: str
    items: List[CartItem]
    subtotal: float
    discount_code: Optional[str]
    discount_amount: float
    discount_percent: float
    total_amount: float
    timestamp: datetime


class UserOrder(BaseModel):
    order_count: int
    orders: List[Order]


class UsedDiscount(BaseModel):
    order_id: str
    discount_code: str
    discount_percent: float
    discount_amount: float
    timestamp: datetime

class Discount(BaseModel):
    discount_code: str
    discount_percent: float


class UserDiscountData(BaseModel):
    available_discount: Optional[Discount]
    used_discounts: List[UsedDiscount]


class AdminStoreStatisticsResponse(BaseModel):
    total_orders: int
    total_items_purchased: int
    average_order_value: float
    total_purchase_amount: float
    total_discount_amount: float
    discount_utilization_rate: float
    discount_codes: List[str]


class GenerateDiscountResponse(BaseModel):
    discount_code: str
    message: str


class GenerateDiscountRequest(BaseModel):
    session_id: str
