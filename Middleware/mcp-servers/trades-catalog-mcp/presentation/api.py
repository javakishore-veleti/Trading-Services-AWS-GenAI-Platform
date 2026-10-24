from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from common.dtos.req_resp_dtos import (
    ErrorDto,
    GetProductRequest,
    GetProductResponse,
    ListProductsRequest,
    ListProductsResponse,
)
from workflows.interfaces import GetProductWf, ListProductsWf
from workflows.object_factory import WorkflowObjectFactory


class CatalogApi:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.router.add_api_route("/products", self.list_products, methods=["GET"], response_model=ListProductsResponse)
        self.router.add_api_route("/products/{product_id}", self.get_product, methods=["GET"], response_model=GetProductResponse)

    def list_products(self, request: Annotated[ListProductsRequest, Depends()]) -> ListProductsResponse:
        workflow: ListProductsWf = WorkflowObjectFactory.list_products()
        response = workflow.invoke(request)
        self._raise_for_error(response.error)
        return response

    def get_product(self, product_id: str) -> GetProductResponse:
        workflow: GetProductWf = WorkflowObjectFactory.get_product()
        response = workflow.invoke(GetProductRequest(product_id=product_id))
        self._raise_for_error(response.error)
        return response

    def _raise_for_error(self, error: ErrorDto | None) -> None:
        if error is None:
            return
        status = 404 if error.code == "not_found" else 400
        raise HTTPException(status_code=status, detail=error.message)
