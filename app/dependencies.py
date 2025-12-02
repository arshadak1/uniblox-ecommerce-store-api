from fastapi import Request, Response
import uuid

from app.repositories.repository import repository
from app.services.admin_service import AdminService
from app.services.cart_service import CartService
from app.services.checkout_service import CheckoutService, DiscountService
from app.services.product_service import ProductService


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
        repository.add_user(session_id)

    return session_id


def get_checkout_service() -> CheckoutService:
    """
    Dependency injection for CheckoutService.
    """
    return CheckoutService(repository)


def get_admin_service() -> AdminService:
    """Dependency injection for AdminService."""
    return AdminService(repository)


def get_discount_service() -> DiscountService:
    """Dependency injection for DiscountService."""
    return DiscountService(repository)


def get_product_service() -> ProductService:
    """Dependency injection for ProductService."""
    return ProductService(repository)
