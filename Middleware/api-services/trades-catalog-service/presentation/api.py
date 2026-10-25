from fastapi import APIRouter, HTTPException

from services.impl.catalogsvc import CatalogError
from services.object_factory import ServiceObjectFactory


class CatalogApi:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.router.add_api_route("/products", self.products, methods=["GET"])
        self.router.add_api_route("/products/{product_id}", self.product, methods=["GET"])
        self.router.add_api_route("/eligibility", self.eligibility, methods=["GET"])
        self.router.add_api_route("/regulatory-references", self.references, methods=["GET"])

    def products(self) -> dict:
        return ServiceObjectFactory.catalog_service().products()

    def product(self, product_id: str) -> dict:
        try:
            return ServiceObjectFactory.catalog_service().product(product_id)
        except CatalogError as exc:
            raise HTTPException(status_code=exc.status, detail=exc.message) from exc

    def eligibility(self, customer_id: str) -> dict:
        return ServiceObjectFactory.catalog_service().eligibility(customer_id)

    def references(self) -> dict:
        return ServiceObjectFactory.catalog_service().references()
