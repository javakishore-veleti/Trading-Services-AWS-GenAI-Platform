from common.dtos.req_resp_dtos import (
    ErrorDto,
    GetProductRequest,
    GetProductResponse,
    ListProductsRequest,
    ListProductsResponse,
)
from dao.object_factory import DaoObjectFactory
from services.interfaces import CatalogSvc


class CatalogSvcImpl(CatalogSvc):
    def list_products(self, request: ListProductsRequest) -> ListProductsResponse:
        rows = DaoObjectFactory.catalog_dao().find_products(request)
        return ListProductsResponse(products=rows.products)

    def get_product(self, request: GetProductRequest) -> GetProductResponse:
        row = DaoObjectFactory.catalog_dao().find_product(request)
        if row.product is None:
            return GetProductResponse(error=ErrorDto(code="not_found", message=f"Unknown product {request.product_id}"))
        return GetProductResponse(product=row.product)
