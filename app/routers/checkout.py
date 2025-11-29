"""
Checkout API endpoints.
Provides RESTful endpoints for order processing and checkout.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated

from app.models.schema import CheckoutRequest, CheckoutResponse
from app.services.checkout_service import CheckoutService
from app.dependencies import get_checkout_service, get_session_id

router = APIRouter(prefix="/checkout", tags=["Checkout"])



@router.post("", response_model=CheckoutResponse, status_code=201)
async def checkout(request: CheckoutRequest, session_id: Annotated[str, Depends(get_session_id)],
                   checkout_service: Annotated[CheckoutService, Depends(get_checkout_service)]) -> CheckoutResponse:
    """
    Process a checkout request.

    This endpoint:
    1. Validates the cart items
    2. Validates the discount code (if provided)
    3. Calculates the total amount with discount
    4. Creates an order
    5. Generates a new discount code if this is the nth order

    - **items**: List of items being purchased (required)
    - **discount_code**: Optional discount code to apply

    Returns order details including:
    - Order ID
    - Subtotal and total amounts
    - Discount information
    - New discount code (if earned)

    **Discount Code Rules:**
    - Every nth order (configurable, default: 3) receives a discount code
    - Discount codes provide 10% off the order total
    - Each code can only be used once
    - Invalid or used codes will result in an error
    """
    try:
        return checkout_service.process_checkout(session_id, discount_code=request.discount_code)
    except ValueError as e:
        # Discount code validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Other unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during checkout: {str(e)}"
        )
