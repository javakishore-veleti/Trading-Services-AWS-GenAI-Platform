from dao.interfaces import CatalogDao
from services.interfaces import CatalogService


class CatalogError(Exception):
    def __init__(self, status: int, message: str) -> None:
        self.status = status
        self.message = message
        super().__init__(message)


class CatalogServiceImpl(CatalogService):
    def __init__(self, dao: CatalogDao) -> None:
        self._dao = dao

    def products(self) -> dict:
        return {"products": self._dao.products()}

    def product(self, product_id: str) -> dict:
        found = self._dao.product(product_id)
        if found is None:
            raise CatalogError(404, "That product is not in the catalog.")
        return found

    def eligibility(self, customer_id: str) -> dict:
        return {"customer_id": customer_id, "products": self._dao.eligibility(customer_id)}

    def references(self) -> dict:
        return {"references": self._dao.references()}
