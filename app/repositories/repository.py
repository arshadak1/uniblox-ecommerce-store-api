"""
In-memory data store for the uniblox-ecommerce-store.
"""

import threading
from typing import Dict, List, Optional


class UnibloxRepository:
    
    def __init__(self):
        """Initialize the repository with empty data structures."""
        # Shopping cart storage
        self._carts: Dict[str, List[Dict]] = {}
        
        # Locks for thread safety
        self._cart_lock = threading.Lock()
    
    def get_cart(self, session_id: str) -> List[Dict]:
        """Get cart items for a session."""
        with self._cart_lock:
            return self._carts.get(session_id, []).copy()

    def add_to_cart(self, session_id: str, item: Dict) -> List[Dict]:
        """Add an item to cart."""
        with self._cart_lock:
            if session_id not in self._carts:
                self._carts[session_id] = []

            # Check if item already exists
            for cart_item in self._carts[session_id]:
                if cart_item['product_id'] == item['product_id']:
                    cart_item['quantity'] += item['quantity']
                    return self._carts[session_id].copy()

            # Add new item
            self._carts[session_id].append(item)
            return self._carts[session_id].copy()


# Global repository instance
repository = UnibloxRepository()
