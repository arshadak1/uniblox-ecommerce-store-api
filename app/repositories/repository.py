"""
In-memory data store for the uniblox-ecommerce-store.
"""

import threading
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from app.models.schema import CartItem, Order, UserOrder, User, UserDiscountData, Discount, UsedDiscount, \
    AdminStoreStatisticsResponse


class UnibloxRepository:
    
    def __init__(self):
        """Initialize the repository with empty data structures."""
        # Users
        self._users: Dict[str, User] = {}

        # Shopping cart storage
        self._carts: Dict[str, List[CartItem]] = {}

        # Order storage
        self._orders: Dict[str, UserOrder] = {}

        # Discount Storage
        self._discount_codes: Dict[str, UserDiscountData] = {}

        # Locks for thread safety
        self._cart_lock = threading.Lock()
        self._order_lock = threading.Lock()
        self._discount_lock = threading.Lock()


    def add_user(self, session_id: str):
        if self._users.get(session_id):
            print("already")
            return
        self._users[session_id] = User(session_id=session_id, date_created=datetime.now())
    
    def get_cart(self, session_id: str) -> List[CartItem]:
        """Get cart items for a session."""
        with self._cart_lock:
            return self._carts.get(session_id, []).copy()

    def add_to_cart(self, session_id: str, item: CartItem) -> List[CartItem]:
        """Add an item to cart."""
        with self._cart_lock:
            if session_id not in self._carts:
                self._carts[session_id] = []

            # Check if item already exists
            for cart_item in self._carts[session_id]:
                if cart_item.product_id == item.product_id:
                    cart_item.quantity += item.quantity
                    return self._carts[session_id].copy()

            # Add new item
            self._carts[session_id].append(item)
            return self._carts[session_id].copy()

    def update_cart_item(self, session_id: str, product_id: int, quantity: int) -> Optional[List[CartItem]]:
        """Update cart item quantity."""
        with self._cart_lock:
            if session_id not in self._carts:
                return None

            for item in self._carts[session_id]:
                if item.product_id == product_id:
                    item.quantity = quantity
                    return self._carts[session_id].copy()

            return None

    def remove_from_cart(self, session_id: str, product_id: int) -> Optional[List[CartItem]]:
        """Remove an item from cart."""
        with self._cart_lock:
            if session_id not in self._carts:
                return None

            self._carts[session_id] = [
                item for item in self._carts[session_id]
                if item.product_id != product_id
            ]
            return self._carts[session_id].copy()

    def clear_cart(self, session_id: str):
        with self._cart_lock:
            if session_id in self._carts:
                del self._carts[session_id]

    def create_order(self, session_id: str, items:List[CartItem], subtotal: float, discount_code: str,
                     discount_amount: float, total_amount: float, discount_percent: float) -> Optional[Order]:
        with self._order_lock:
            if not items:
                return None
            order = Order(order_id=str(uuid.uuid4()), items=items, subtotal=subtotal, discount_code=discount_code,
                          discount_amount=discount_amount, total_amount=total_amount, discount_percent=discount_percent,
                          timestamp=datetime.now())
            if session_id not in self._orders:
                self._orders[session_id] = UserOrder(order_count=0, orders=[])
            self._orders[session_id].order_count += 1
            self._orders[session_id].orders.append(order)
            return order

    def mark_discount_code_used(self, session_id: str, order: Order):
        with self._discount_lock:
            if session_id not in self._discount_codes:
                self._discount_codes[session_id] = UserDiscountData(available_discount=None,
                                                                    used_discounts=[])
                return
            self._discount_codes[session_id].available_discount = None
            used_discount_code = UsedDiscount(order_id=order.order_id, discount_code=order.discount_code,
                                              discount_percent=order.discount_percent,
                                              discount_amount=order.discount_amount, timestamp=order.timestamp)
            self._discount_codes[session_id].used_discounts.append(used_discount_code)

    def get_discount_code(self, session_id: str, discount_code: str) -> Optional[Discount]:
        with self._discount_lock:
            if session_id not in self._discount_codes:
                return None
            available_discount = self._discount_codes[session_id].available_discount
            if not available_discount or available_discount.discount_code != discount_code:
                return None
            return available_discount

    def get_user_orders(self, session_id: str) -> Optional[UserOrder]:
        if session_id not in self._orders:
            return None
        return self._orders[session_id]

    def create_discount_code(self, session_id: str, discount_code: str, discount_percent: str):
        with self._discount_lock:
            if session_id not in self._discount_codes:
                self._discount_codes[session_id] = UserDiscountData(available_discount=None,
                                                                    used_discounts=[])
            if self._discount_codes[session_id].available_discount is None:
                self._discount_codes[session_id].available_discount = Discount(discount_code=discount_code,
                                                                               discount_percent=discount_percent)
            return self._discount_codes[session_id].available_discount.discount_code

    def get_statistics(self) -> AdminStoreStatisticsResponse:
        """
        Calculate comprehensive statistics.

        Returns:
            Dictionary containing various statistics
        """
        with self._order_lock, self._discount_lock:
            orders = []
            total_orders = 0
            total_items = 0

            for entry in self._orders.values():
                # order_count (safe even if None)
                total_orders += entry.order_count or 0

                # orders list (safe even if None)
                user_orders = entry.orders or []
                total_items += len(user_orders)
                orders.extend(user_orders)

            # Now compute totals across all collected orders
            total_amount = sum(o.total_amount for o in orders)
            total_discount = sum(o.discount_amount for o in orders)

            avg_order_value = total_amount / total_orders if total_orders else 0.0

            total_discounts = 0
            used_discounts = 0
            discount_codes = []
            for discount_data in self._discount_codes.values():
                if discount_data.available_discount:
                    total_discounts += 1
                    discount_codes.append(discount_data.available_discount.discount_code)

                total_discounts += len(discount_data.used_discounts or [])
                used_discounts += len(discount_data.used_discounts or [])
                for discount in discount_data.used_discounts:
                    discount_codes.append(discount.discount_code)

            utilization_rate = (used_discounts / total_discounts * 100) if total_discounts > 0 else 0.0

            return AdminStoreStatisticsResponse(
                total_orders=total_orders,
                total_items_purchased=total_items,
                total_purchase_amount=round(total_amount, 2),
                total_discount_amount=round(total_discount, 2),
                average_order_value=round(avg_order_value, 2),
                discount_utilization_rate=round(utilization_rate, 2),
                discount_codes=discount_codes
            )

    def get_users(self) -> List[User]:
        return self._users.values()

    def is_discount_already_used(self, session_id: str, discount_code: str) -> bool:
        if session_id not in self._discount_codes:
            return False
        for discount in self._discount_codes[session_id].used_discounts:
            if discount.discount_code == discount_code:
                return True
        return False


# Global repository instance
repository = UnibloxRepository()
