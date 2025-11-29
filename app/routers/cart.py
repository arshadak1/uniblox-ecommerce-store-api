"""
Cart Related API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated

from app.models.schema import CartResponse, AddToCartRequest, UpdateCartRequest
from app.services.cart_service import CartService
from app.dependencies import get_cart_service, get_session_id

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("", response_model=CartResponse)
async def get_cart(cart_service: Annotated[CartService, Depends(get_cart_service)],
                   session_id: Annotated[str, Depends(get_session_id)]) -> CartResponse:
    """
    Get the current cart contents.
    
    Returns all items in the cart with totals.
    """
    try:
        return cart_service.get_cart(session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/add", response_model=CartResponse, status_code=201)
async def add_to_cart(request: AddToCartRequest, cart_service: Annotated[CartService, Depends(get_cart_service)],
                      session_id: Annotated[str, Depends(get_session_id)]) -> CartResponse:
    """
    Add an item to the shopping cart.

    - **product_id**: Unique identifier for the product
    - **name**: Product name
    - **price**: Product price (must be positive)
    - **quantity**: Quantity to add (must be positive, defaults to 1)

    Returns the updated cart with all items.
    """
    try:
        return cart_service.add_to_cart(
            session_id=session_id,
            product_id=request.product_id,
            name=request.name,
            price=request.price,
            quantity=request.quantity
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/update", response_model=CartResponse)
async def update_cart_item(request: UpdateCartRequest, cart_service: Annotated[CartService, Depends(get_cart_service)],
                           session_id: Annotated[str, Depends(get_session_id)]) -> CartResponse:
    """
    Update the quantity of an item in the cart.

    - **product_id**: ID of the product to update
    - **quantity**: New quantity (must be positive)

    Returns the updated cart.
    """
    try:
        return cart_service.update_cart_item(
            session_id=session_id,
            product_id=request.product_id,
            quantity=request.quantity
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/remove/{product_id}", response_model=CartResponse)
async def remove_from_cart(product_id: int, cart_service: Annotated[CartService, Depends(get_cart_service)],
                           session_id: Annotated[str, Depends(get_session_id)]) -> CartResponse:
    """
    Remove an item from the cart.

    - **product_id**: ID of the product to remove

    Returns the updated cart.
    """
    try:
        return cart_service.remove_from_cart(session_id=session_id, product_id=product_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("", status_code=204)
async def clear_cart(cart_service: Annotated[CartService, Depends(get_cart_service)],
                     session_id: Annotated[str, Depends(get_session_id)]):
    """
    Clears cart.
    """
    try:
        cart_service.clear_cart(session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))