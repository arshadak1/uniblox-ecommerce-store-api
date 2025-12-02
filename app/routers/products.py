"""
Checkout API endpoints.
Provides RESTful endpoints for order processing and checkout.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated, List

from app.models.schema import ProductsResponse
from app.services.product_service import ProductService
from app.dependencies import get_product_service

router = APIRouter(prefix="/products", tags=["Products"])



@router.get("", response_model=ProductsResponse, status_code=201)
async def get_products(product_service: Annotated[ProductService, Depends(get_product_service)]) -> ProductsResponse:
    """
        Fetches available products.
        Returns list of Products
    """
    try:
        return product_service.get_products()
    except ValueError as e:
        # Discount code validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Other unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during checkout: {str(e)}"
        )
