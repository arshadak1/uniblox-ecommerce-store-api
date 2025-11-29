"""
Unit tests for checkout functionality.
Tests the checkout service and API endpoints.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.repositories.repository import UnibloxRepository
from app.services.cart_service import CartService
from app.services.checkout_service import CheckoutService, DiscountService
from app.models.schema import CartItem


@pytest_asyncio.fixture
async def client():
    """Provide an async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def clear_cart(client):
    """Clear cart before and after each test."""
    await client.delete("/api/v1/cart")
    yield
    await client.delete("/api/v1/cart")


@pytest.mark.asyncio
class TestCheckoutAPI:
    """Test suite for Checkout API endpoints."""

    async def test_checkout_without_discount(self, client, clear_cart):
        """Test successful checkout without discount code."""
        await client.post(
            "/api/v1/cart/add",
            json={
                "product_id": 1,
                "name": "Test Product",
                "price": 100,
                "quantity": 2
            }
        )
        response = await client.post(
            "/api/v1/checkout",
            json={
                "discount_code": ""
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["subtotal"] == 200.00
        assert data["total_amount"] == 200.00
        assert data["discount_applied"] is False
        assert data["discount_amount"] == 0.0
        assert "order_id" in data

    async def test_checkout_from_cart(self, client, clear_cart):
        """Test checkout using items from session cart."""
        # Add items to cart first
        await client.post(
            "/api/v1/cart/add",
            json={
                "product_id": 1,
                "name": "Product 1",
                "price": 100.00,
                "quantity": 1
            }
        )

        # Checkout using cart
        response = await client.post(
            "/api/v1/checkout",
            json={
                "discount_code": ""
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["subtotal"] == 100.00
        assert data["total_amount"] == 100.00

        # Verify cart is cleared
        cart_response = await client.get("/api/v1/cart")
        cart_data = cart_response.json()
        assert len(cart_data["items"]) == 0

    async def test_checkout_empty_cart_fails(self, client, clear_cart):
        """Test that checkout fails with empty cart."""
        response = await client.post(
            "/api/v1/checkout",
            json={
                "discount_code": ""
            }
        )

        assert response.status_code == 400
        assert "cart is empty" in response.json()["detail"].lower()

    async def test_checkout_with_valid_discount(self, client, clear_cart):
        """Test checkout with valid discount code."""
        # First, generate a discount code
        await client.post(
            "/api/v1/cart/add",
            json={
                "product_id": 1,
                "name": "Product 1",
                "price": 100.00,
                "quantity": 1
            }
        )
        discount_response = await client.post(
            "/api/v1/admin/generate-discount",
            json={
                "session_id": client.cookies.get("session_id")
            }
        )
        discount_code = discount_response.json()["discount_code"]

        # Use the discount code
        response = await client.post(
            "/api/v1/checkout",
            json={
                "discount_code": discount_code
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["discount_applied"] is True
        assert data["discount_amount"] == 10.00  # 10% of 100
        assert data["total_amount"] == 90.00

    async def test_checkout_with_invalid_discount(self, client, clear_cart):
        """Test checkout with invalid discount code."""
        await client.post(
            "/api/v1/cart/add",
            json={
                "product_id": 1,
                "name": "Product 1",
                "price": 100.00,
                "quantity": 1
            }
        )
        response = await client.post(
            "/api/v1/checkout",
            json={
                "discount_code": "INVALID123"
            }
        )

        assert response.status_code == 400
        assert "Invalid discount code" in response.json()["detail"]

    async def test_checkout_with_used_discount(self, client, clear_cart):
        """Test checkout with already used discount code."""
        await client.post(
            "/api/v1/cart/add",
            json={
                "product_id": 1,
                "name": "Product 1",
                "price": 100.00,
                "quantity": 1
            }
        )
        # Generate discount code
        discount_response = await client.post(
            "/api/v1/admin/generate-discount",
            json={"session_id": client.cookies.get("session_id")}
        )
        print(client.cookies.get("session_id"))
        discount_code = discount_response.json()["discount_code"]

        # Use it once
        await client.post(
            "/api/v1/checkout",
            json={
                "discount_code": discount_code
            }
        )

        await client.post(
            "/api/v1/cart/add",
            json={
                "product_id": 1,
                "name": "Product 1",
                "price": 100.00,
                "quantity": 1
            }
        )
        print(client.cookies.get("session_id"))

        # Try to use it again
        response = await client.post(
            "/api/v1/checkout",
            json={
                "discount_code": discount_code
            }
        )

        print(client.cookies.get("session_id"))
        assert response.status_code == 400
        assert "already been used" in response.json()["detail"].lower()

    async def test_checkout_generates_discount_on_nth_order(self, client, clear_cart):
        """Test that discount code is generated on every 3rd order."""
        from app import config
        config.settings.NTH_ORDER_DISCOUNT = 3
        # Place 2 orders
        for i in range(2):
            response = await client.post(
                "/api/v1/cart/add",
                json={
                    "product_id": i + 1,
                    "name": f"Product {i + 1}",
                    "price": 100.00,
                    "quantity": 1
                }
            )
            print(response.json())
            response = await client.post(
                "/api/v1/checkout",
                json={
                    "discount_code": ""
                }
            )
            data = response.json()
            print(response.json())
            assert data["new_discount_code"] is None

        await client.post(
            "/api/v1/cart/add",
            json={
                "product_id": 4,
                "name": f"Product 4",
                "price": 100.00,
                "quantity": 1
            }
        )
        # 3rd order should generate discount
        response = await client.post(
            "/api/v1/checkout",
            json={
                "discount_code": ""
            }
        )

        data = response.json()
        assert data["new_discount_code"] is not None
        assert "SAVE10" in data["new_discount_code"]
