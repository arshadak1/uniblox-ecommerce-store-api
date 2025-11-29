"""
Cart Related API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Response
from typing import Annotated
import uuid

from app.models.schema import CartResponse
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
