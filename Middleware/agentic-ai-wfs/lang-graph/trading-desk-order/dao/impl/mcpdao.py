from fastmcp import Client

from dao.interfaces import McpToolDao


class McpToolDaoImpl(McpToolDao):
    """The only class that calls an MCP server."""

    SERVERS = {
        'trades-orders-mcp': 'http://127.0.0.1:8103/mcp',
    }

    async def call_tool(self, server: str, tool: str, arguments: dict) -> dict:
        url = self.SERVERS.get(server)
        if url is None:
            return {"error": {"code": "invalid", "message": f"Unknown MCP server {server}"}}
        try:
            async with Client(url) as client:
                result = await client.call_tool(tool, {"request": arguments}, raise_on_error=False)
        except Exception as exc:
            return {"error": {"code": "unavailable", "message": f"{server} {tool} failed: {exc}"}}
        data = getattr(result, "data", None)
        if hasattr(data, "model_dump"):
            return data.model_dump()
        if isinstance(data, dict):
            return data
        structured = getattr(result, "structured_content", None)
        if isinstance(structured, dict):
            return structured
        return {"error": {"code": "invalid", "message": f"{server} {tool} returned no record"}}
