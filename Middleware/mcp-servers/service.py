"""Process host shared by the MCP servers. One class, no free functions."""

from fastapi import APIRouter, FastAPI
from fastmcp import FastMCP


class ProcessHost:
    def __init__(self, service_name: str, mcp: FastMCP, router: APIRouter) -> None:
        self._service_name = service_name
        self._mcp = mcp
        self._router = router

    def build(self) -> FastAPI:
        mcp_app = self._mcp.http_app(path="/", stateless_http=True)
        app = FastAPI(title=self._service_name, lifespan=mcp_app.lifespan)
        app.add_api_route("/health", self.health, methods=["GET"])
        app.include_router(self._router)
        app.mount("/mcp", mcp_app)
        return app

    def health(self) -> dict[str, str]:
        return {"status": "ok", "service": self._service_name}
