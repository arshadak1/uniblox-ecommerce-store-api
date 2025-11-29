"""
Cart Related API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Response
from typing import Annotated
import uuid

from app.models.schema import CartResponse, AddToCartRequest, UpdateCartRequest
from app.services.cart_service import CartService
from app.repositories.repository import repository

router = APIRouter(prefix="/cart", tags=["Cart"])


def get_cart_service() -> CartService:
    """
    Dependency injection for CartService.
    """
    return CartService(repository)


def get_session_id(request: Request, response: Response) -> str:
    session_id = request.cookies.get("session_id")

    if session_id is None:
        session_id = str(uuid.uuid4())
        response.set_cookie(key="session_id", value=session_id, httponly=True)

    return session_id


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