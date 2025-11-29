"""
Async unit tests for cart functionality.
Uses httpx.AsyncClient for FastAPI TestClient.
"""

import pytest
import pytest_asyncio
import math
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest_asyncio.fixture
async def clear_cart():
    """Clear cart before and after each test."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        await client.delete("/api/v1/cart")
    yield
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        await client.delete("/api/v1/cart")


@pytest_asyncio.fixture
async def client():
    """Provide an async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


# Use asyncio tests
@pytest.mark.asyncio
class TestCartAPI:
    """Test suite for Cart API endpoints."""

    async def test_add_to_cart_success(self, client, clear_cart):
        response = await client.post(
            "/api/v1/cart/add",
            json={
                "product_id": 1,
                "name": "Test Product",
                "price": 99.99,
                "quantity": 2
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["total_items"] == 2
        assert math.isclose(data["subtotal"], 199.98, rel_tol=1e-2)
        assert len(data["items"]) == 1
        assert data["items"][0]["product_id"] == 1

    async def test_add_to_cart_invalid_price(self, client, clear_cart):
        response = await client.post(
            "/api/v1/cart/add",
            json={
                "product_id": 1,
                "name": "Test Product",
                "price": -10,  # Invalid negative price
                "quantity": 1
            }
        )
        assert response.status_code == 422

    async def test_add_to_cart_invalid_quantity(self, client, clear_cart):
        response = await client.post(
            "/api/v1/cart/add",
            json={
                "product_id": 1,
                "name": "Test Product",
                "price": 99.99,
                "quantity": 0
            }
        )
        assert response.status_code == 422

    async def test_update_cart_item(self, client, clear_cart):
        # First add an item
        await client.post(
            "/api/v1/cart/add",
            json={
                "product_id": 2,
                "name": "Another Product",
                "price": 50.00,
                "quantity": 1
            }
        )
        # Update quantity
        response = await client.put(
            "/api/v1/cart/update",
            json={"product_id": 2, "quantity": 5}
        )
        assert response.status_code == 200
        data = response.json()
        item = next(i for i in data["items"] if i["product_id"] == 2)
        assert item["quantity"] == 5

    async def test_update_nonexistent_item(self, client, clear_cart):
        response = await client.put(
            "/api/v1/cart/update",
            json={"product_id": 9999, "quantity": 1}
        )
        assert response.status_code == 404

    async def test_remove_from_cart(self, client, clear_cart):
        # Add item
        await client.post(
            "/api/v1/cart/add",
            json={
                "product_id": 3,
                "name": "Product to Remove",
                "price": 25.00,
                "quantity": 1
            }
        )
        # Remove item
        response = await client.delete("/api/v1/cart/remove/3")
        assert response.status_code == 200
        data = response.json()
        assert not any(i["product_id"] == 3 for i in data["items"])

    async def test_get_cart(self, client, clear_cart):
        response = await client.get("/api/v1/cart")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total_items" in data
        assert "subtotal" in data

    async def test_clear_cart(self, client, clear_cart):
        # Add some items
        await client.post(
            "/api/v1/cart/add",
            json={
                "product_id": 4,
                "name": "Product 1",
                "price": 10.00,
                "quantity": 1
            }
        )
        # Clear cart
        response = await client.delete("/api/v1/cart")
        assert response.status_code == 204

        # Verify cart is empty
        response = await client.get("/api/v1/cart")
        data = response.json()
        assert len(data["items"]) == 0
        assert data["total_items"] == 0
