"""
Cart service containing business logic for shopping cart operations.
Handles adding, updating, and removing items from the cart.
"""

import logging
from typing import Dict, List
from app.repositories.repository import UnibloxRepository
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

    def _build_cart_response(self, cart_items: List[Dict]) -> CartResponse:
        """
        Build a CartResponse from raw cart data.

        Args:
            cart_items: List of cart item dictionaries

        Returns:
            Formatted cart response
        """
        items = [CartItem(**item) for item in cart_items]
        total_items = sum(item.quantity for item in items)
        subtotal = sum(item.price * item.quantity for item in items)

        return CartResponse(items=items, total_items=total_items, subtotal=round(subtotal, 2))
