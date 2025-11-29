"""
Cart service containing business logic for shopping cart operations.
Handles adding, updating, and removing items from the cart.
"""

import logging
from typing import Dict, List
from app.repositories.repository import UnibloxRepository, repository
from app.models.schema import CartItem, CartResponse

logger = logging.getLogger(__name__)


class CartService:
    """Service layer for managing shopping cart operations."""
    
    def __init__(self, repository: UnibloxRepository):
        """
        Initialize the cart service.
        
        Args:
            repository: Data repository instance
        """
        self.repository = repository
    
    def get_cart(self, session_id: str) -> CartResponse:
        """
        Get the current cart contents.
        
        Args:
            session_id: User session identifier
            
        Returns:
            Current cart response
        """
        cart_items = self.repository.get_cart(session_id)
        return self._build_cart_response(cart_items)

    def add_to_cart(self, session_id: str, product_id: int, name: str, price: float, quantity: int) -> CartResponse:
        """
        Add an item to the shopping cart.

        Args:
            session_id: User session identifier
            product_id: Product id to add
            name: Product name
            price: Product price
            quantity: Quantity to add

        Returns:
            Updated cart response
        """
        logger.info(
            f"Adding to cart - Session: {session_id}, "
            f"Product: {product_id}, Quantity: {quantity}"
        )

        item = CartItem(product_id=product_id, name=name, price=round(price, 2), quantity=quantity)

        cart_items = self.repository.add_to_cart(session_id, item)
        return self._build_cart_response(cart_items)

    def update_cart_item(self, session_id: str, product_id: int, quantity: int) -> CartResponse:
        """
        Update the quantity of an item in the cart.

        Args:
            session_id: User session identifier
            product_id: Product ID to update
            quantity: quantity to update

        Returns:
            Updated cart response

        Raises:
            ValueError: If item not found in cart
        """
        logger.info(
            f"Updating cart - Session: {session_id}, "
            f"Product: {product_id}, New Quantity: {quantity}"
        )

        cart_items = self.repository.update_cart_item(
            session_id,
            product_id,
            quantity
        )

        if cart_items is None:
            raise ValueError(f"Product {product_id} not found in cart")

        return self._build_cart_response(cart_items)

    def remove_from_cart(self, session_id: str, product_id: int) -> CartResponse:
        """
        Remove an item from the cart.

        Args:
            session_id: User session identifier
            product_id: Product ID to remove

        Returns:
            Updated cart response

        Raises:
            ValueError: If item not found in cart
        """
        logger.info(
            f"Removing from cart - Session: {session_id}, Product: {product_id}"
        )

        cart_items = self.repository.remove_from_cart(session_id, product_id)

        if cart_items is None:
            raise ValueError(f"Product {product_id} not found in cart")

        return self._build_cart_response(cart_items)

    def clear_cart(self, session_id: str):
        self.repository.clear_cart(session_id)

    def _build_cart_response(self, items: List[CartItem]) -> CartResponse:
        """
        Build a CartResponse from raw cart data.

        Args:
            items: List of cart items

        Returns:
            Formatted cart response
        """
        total_items = sum(item.quantity for item in items)
        subtotal = sum(item.price * item.quantity for item in items)

        return CartResponse(items=items, total_items=total_items, subtotal=round(subtotal, 2))
