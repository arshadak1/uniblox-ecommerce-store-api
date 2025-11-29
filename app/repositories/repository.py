"""
In-memory data store for the uniblox-ecommerce-store.
"""

import threading
from typing import Dict, List


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


# Global repository instance
repository = UnibloxRepository()
