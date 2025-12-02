from typing import List

from app.models.schema import ProductsResponse, Product
from app.repositories.repository import UnibloxRepository


class ProductService:
    def __init__(self, repository: UnibloxRepository):
        self.repository = repository

    def get_products(self) -> ProductsResponse:
        products: List[Product] = self.repository.get_products()
        return ProductsResponse(products=products)
