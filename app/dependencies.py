from fastapi import Request, Response
import uuid

from app.repositories.repository import repository
from app.services.cart_service import CartService



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

