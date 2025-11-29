"""
Checkout service containing business logic for order processing.
Handles discount validation, order creation, and discount code generation.
"""

import logging
import secrets
import string
from typing import List, Optional

from app.repositories.repository import UnibloxRepository, repository
from app.models.schema import CartItem, CheckoutResponse
from app.config import settings


logger = logging.getLogger(__name__)


class CheckoutService:
    """Service class for managing checkout and order operations."""

    def __init__(self, repository: UnibloxRepository):
        """
        Initialize the checkout service.

        Args:
            repository: Data repository instance
        """
        self.repository = repository
        self.nth_order = settings.NTH_ORDER_DISCOUNT
        self.discount_percentage = settings.DISCOUNT_PERCENTAGE

    def process_checkout(self, session_id: str, discount_code: Optional[str]) -> CheckoutResponse | None:
        """
        Process a checkout request with optional discount code.

        Args:
            session_id: User session id
            discount_code: Optional discount code to apply

        Returns:
            Checkout response with order details

        Raises:
            ValueError: If discount code is invalid or already used
        """
        items = repository.get_cart(session_id)
        if not items:
            raise ValueError("Cart is empty")
        logger.info(
            f"Processing checkout - Items: {len(items)}, "
            f"Discount Code: {discount_code or 'None'}"
        )
        # Calculate subtotal
        subtotal = self._calculate_subtotal(items)

        # Validate and apply discount
        discount_amount = 0.0
        discount_applied = False

        if discount_code:
            discount_amount = self._validate_and_apply_discount(session_id, discount_code, subtotal)
            discount_applied = True

        # Calculate total
        total_amount = subtotal - discount_amount

        # Create order
        order = self.repository.create_order(
            session_id=session_id,
            items=items,
            subtotal=subtotal,
            discount_code=discount_code,
            discount_amount=discount_amount,
            discount_percent=self.discount_percentage,
            total_amount=total_amount
        )

        # Mark discount code as used if applied
        if discount_applied and discount_code:
            self.repository.mark_discount_code_used(session_id, order)

        # Check if this order qualifies for a new discount code
        new_discount_code = self._check_and_generate_discount(session_id)

        logger.info(
            f"Order created - ID: {order.order_id}, "
            f"Total: ${total_amount:.2f}, "
            f"New Discount: {new_discount_code or 'None'}"
        )

        # Build response
        message = "Order placed successfully!"
        if new_discount_code:
            message += f" You've earned a discount code: {new_discount_code}"
        self.repository.clear_cart(session_id)

        return CheckoutResponse(
            order_id=order.order_id,
            subtotal=round(subtotal, 2),
            discount_applied=discount_applied,
            discount_amount=round(discount_amount, 2),
            total_amount=round(total_amount, 2),
            new_discount_code=new_discount_code,
            message=message,
            timestamp=order.timestamp
        )

    def _calculate_subtotal(self, items: List[CartItem]) -> float:
        """
        Calculate the subtotal of all items.

        Args:
            items: List of cart items

        Returns:
            Subtotal amount
        """
        return sum(item.price * item.quantity for item in items)

    def _validate_and_apply_discount(self, session_id: str, discount_code: str, subtotal: float) -> float:
        """
        Validate a discount code and calculate discount amount.

        Args:
            discount_code: Code to validate
            subtotal: Order subtotal

        Returns:
            Discount amount to apply

        Raises:
            ValueError: If code is invalid or already used
        """
        if self.repository.is_discount_already_used(session_id, discount_code):
            raise ValueError("Already been used")

        discount = self.repository.get_discount_code(session_id, discount_code)


        if not discount:

            raise ValueError("Invalid discount code")

        # Calculate discount
        discount_amount = subtotal * (discount.discount_percent / 100)

        logger.info(
            f"Discount applied - Code: {discount_code}, "
            f"Amount: ${discount_amount:.2f}"
        )

        return discount_amount

    def _check_and_generate_discount(self, session_id: str) -> Optional[str]:
        """
        Check if this order qualifies for a discount code and generate one.

        Args:
            session_id: The order ID to check

        Returns:
            Generated discount code or None
        """
        # Check if this is the nth order
        user_order = repository.get_user_orders(session_id)
        if user_order and user_order.order_count % self.nth_order == 0 and user_order.order_count > 0:
            discount_code = DiscountService.generate_discount_code()
            discount_code = self.repository.create_discount_code(session_id, discount_code, self.discount_percentage)

            logger.info(
                f"Discount code generated: {discount_code}"
            )

            return discount_code

        return None


class DiscountService:
    """Service for managing discount codes (admin operations)."""

    def __init__(self, repository: UnibloxRepository):
        """
        Initialize the discount service.

        Args:
            repository: Data repository instance
        """
        self.repository = repository
        self.discount_percentage = settings.DISCOUNT_PERCENTAGE

    def generate_discount_code_for_user(self, session_id: str) -> str:
        """
        Manually generate a discount code (admin function).

        Returns:
            Generated discount code
        """
        logger.info("Manually generating discount code")

        discount_code = self.generate_discount_code()

        # Store it
        discount_code = self.repository.create_discount_code(session_id, discount_code, self.discount_percentage)

        logger.info(f"Discount code generated: {discount_code}")

        return discount_code


    @staticmethod
    def generate_discount_code() -> str:
        """
        Generate a unique discount code.

        Returns:
            Generated discount code
        """
        # Generate random alphanumeric string
        random_part = ''.join(
            secrets.choice(string.ascii_uppercase + string.digits)
            for _ in range(settings.DISCOUNT_CODE_LENGTH)
        )

        return f"{settings.DISCOUNT_CODE_PREFIX}{random_part}"
