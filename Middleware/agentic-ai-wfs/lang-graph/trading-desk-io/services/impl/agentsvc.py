from business.object_factory import BusinessObjectFactory
from common.dtos import InvokeRequest, StoredSlice
from dao.object_factory import DaoObjectFactory
from services.interfaces import AgentSvc


class AgentSvcImpl(AgentSvc):
    """Context stays out of the graph. Redis holds the full record. The parent sees a summary and the latest preview."""

    def _request_key(self, agent: str, context_id: str) -> str:
        return f"lg:{agent}:{context_id}:request"

    def _full_key(self, agent: str, context_id: str, sub_agent: str) -> str:
        return f"lg:{agent}:{context_id}:{sub_agent}:full"

    def _slice_key(self, agent: str, context_id: str, sub_agent: str) -> str:
        return f"lg:{agent}:{context_id}:{sub_agent}"

    def _parent_key(self, agent: str, context_id: str) -> str:
        return f"lg:{agent}:{context_id}:agent"

    async def externalize(self, agent: str, request: InvokeRequest) -> None:
        await DaoObjectFactory.context_dao().save(
            self._request_key(agent, request.context_id),
            {"tool": request.tool, "arguments": request.arguments},
        )

    async def isolate(self, agent: str, context_id: str, sub_agent: str) -> str | None:
        raw = await DaoObjectFactory.context_dao().load(self._request_key(agent, context_id))
        if raw is None:
            return "The request was not stored."
        await DaoObjectFactory.context_dao().save(self._slice_key(agent, context_id, sub_agent), raw)
        await DaoObjectFactory.context_dao().delete(self._request_key(agent, context_id))
        return None

    async def load_skill(self, agent: str, context_id: str, sub_agent: str) -> str | None:
        text = DaoObjectFactory.skill_dao().load(agent)
        if text is None:
            return f"No skill file for {agent}."
        stored = await DaoObjectFactory.context_dao().load(self._slice_key(agent, context_id, sub_agent)) or {}
        stored["skill"] = agent
        stored["instructions"] = text
        await DaoObjectFactory.context_dao().save(self._slice_key(agent, context_id, sub_agent), stored)
        return None

    async def select_and_call(self, agent: str, context_id: str, sub_agent: str, tool: str) -> str | None:
        biz = BusinessObjectFactory.agent_biz(agent)
        if biz is None:
            return f"Unknown agent {agent}."
        server = biz.server_for(tool)
        if server is None:
            return f"{agent} cannot call {tool}."
        stored = await DaoObjectFactory.context_dao().load(self._slice_key(agent, context_id, sub_agent))
        arguments = biz.select(tool, (stored or {}).get("arguments") or {})
        result = await DaoObjectFactory.mcp_dao().call_tool(server, tool, arguments)
        await DaoObjectFactory.context_dao().save(
            self._full_key(agent, context_id, sub_agent),
            {"tool": tool, "arguments": arguments, "result": result},
        )
        return None

    async def compress(self, agent: str, context_id: str, sub_agent: str, tool: str) -> str | None:
        biz = BusinessObjectFactory.agent_biz(agent)
        if biz is None:
            return f"Unknown agent {agent}."
        full = await DaoObjectFactory.context_dao().load(self._full_key(agent, context_id, sub_agent))
        summary, preview = biz.compress(sub_agent, (full or {}).get("result") or {})
        existing = await DaoObjectFactory.context_dao().load(self._slice_key(agent, context_id, sub_agent)) or {}
        preview_record = {
            "summary": f"{tool}: {summary}",
            "body": preview,
            "full_key": self._full_key(agent, context_id, sub_agent),
            "skill": agent,
        }
        sub_agent_record = dict(preview_record)
        if existing.get("instructions"):
            sub_agent_record["instructions"] = existing["instructions"]
        await DaoObjectFactory.context_dao().save(self._slice_key(agent, context_id, sub_agent), sub_agent_record)
        parent = await DaoObjectFactory.context_dao().load(self._parent_key(agent, context_id)) or {"older": [], "recent": None}
        older = list(parent.get("older") or [])
        previous = parent.get("recent")
        if isinstance(previous, dict) and previous.get("summary"):
            older.append(previous["summary"])
        await DaoObjectFactory.context_dao().save(
            self._parent_key(agent, context_id),
            {"older": older, "recent": preview_record},
        )
        return None

    async def read_parent(self, agent: str, context_id: str) -> StoredSlice | None:
        stored = await DaoObjectFactory.context_dao().load(self._parent_key(agent, context_id))
        if stored is None:
            return None
        recent = stored.get("recent") or {}
        older = stored.get("older") or []
        summary = recent.get("summary") or ""
        if older:
            summary = "Earlier: " + "; ".join(str(item) for item in older) + ". Latest: " + summary
        return StoredSlice(summary=summary, body=recent.get("body") or {})

    async def retrieve(self, agent: str, context_id: str, sub_agent: str) -> dict | None:
        return await DaoObjectFactory.context_dao().load(self._full_key(agent, context_id, sub_agent))
