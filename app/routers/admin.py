"""
Admin API endpoints.
Provides administrative functionality for managing the store.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated, Dict, List

from app.models.schema import (
    AdminStoreStatisticsResponse,
    GenerateDiscountResponse, GenerateDiscountRequest, User
)
from app.services.admin_service import AdminService
from app.services.checkout_service import DiscountService
from app.dependencies import get_admin_service, get_discount_service

router = APIRouter(prefix="/admin", tags=["Admin"])




@router.get("/stats", response_model=AdminStoreStatisticsResponse)
async def get_statistics(
        admin_service: Annotated[AdminService, Depends(get_admin_service)]
) -> AdminStoreStatisticsResponse:
    """
    Get comprehensive store statistics.

    Returns:
    - **total_orders**: Total number of orders placed
    - **total_items_purchased**: Total items sold across all orders
    - **total_purchase_amount**: Total revenue (after discounts)
    - **total_discount_amount**: Total amount discounted
    - **discount_codes**: List of all discount codes with usage status
    - **average_order_value**: Average order value
    - **discount_utilization_rate**: Percentage of discount codes used

    This endpoint provides a complete overview of store performance.
    """
    try:
        return admin_service.get_statistics()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )


@router.post("/generate-discount", response_model=GenerateDiscountResponse, status_code=201)
async def generate_discount_code(request: GenerateDiscountRequest,
                                 discount_service: Annotated[DiscountService, Depends(get_discount_service)]
                                 ) -> GenerateDiscountResponse:
    """
    Manually generate a discount code.

    This is an admin function to create discount codes outside the normal
    "every nth order" flow. Useful for:
    - Promotional campaigns
    - Customer service compensation
    - Special events

    Returns the generated discount code.

    **Note:** Normally, discount codes are automatically generated for every
    nth order (configured in settings). This endpoint allows manual generation.
    """
    try:
        code = discount_service.generate_discount_code_for_user(request.session_id)
        return GenerateDiscountResponse(
            discount_code=code,
            message="Discount code generated successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate discount code: {str(e)}"
        )


@router.get("/users", response_model=List[User])
def get_users(admin_service: Annotated[AdminService, Depends(get_admin_service)]) -> List[User]:
    try:
        return admin_service.get_users()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch users: {str(e)}"
        )
