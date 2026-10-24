from typing import TypedDict

from langgraph.graph import END, StateGraph

from business.object_factory import BusinessObjectFactory
from common.dtos import InvokeRequest, InvokeResponse
from services.object_factory import ServiceObjectFactory
from workflows.interfaces import DeskAgentWf


class GraphState(TypedDict):
    agent: str
    context_id: str
    tool: str
    sub_agent: str
    error: str


class _DeskGraph(DeskAgentWf):
    """Parent workflow. It is the only caller of this desk's sub-agents."""

    agent_name = ""
    _compiled = None

    def graph(self):
        if type(self)._compiled is None:
            builder = StateGraph(GraphState)
            builder.add_node("isolate", self.isolate)
            builder.add_node("load_skill", self.load_skill)
            builder.add_node("select", self.select)
            builder.add_node("compress", self.compress)
            builder.set_entry_point("isolate")
            builder.add_edge("isolate", "load_skill")
            builder.add_edge("load_skill", "select")
            builder.add_edge("select", "compress")
            builder.add_edge("compress", END)
            type(self)._compiled = builder.compile()
        return type(self)._compiled

    async def isolate(self, state: GraphState) -> dict:
        biz = BusinessObjectFactory.agent_biz(state["agent"])
        if biz is None:
            return {"sub_agent": "", "error": f"Unknown agent {state['agent']}."}
        reason = biz.reject(state["tool"])
        if reason:
            return {"sub_agent": "", "error": reason}
        sub_agent = biz.sub_agent(state["tool"]) or ""
        if not sub_agent:
            return {"sub_agent": "", "error": f"{state['agent']} cannot call {state['tool']}."}
        moved = await ServiceObjectFactory.agent_svc().isolate(state["agent"], state["context_id"], sub_agent)
        if moved:
            return {"sub_agent": sub_agent, "error": moved}
        return {"sub_agent": sub_agent, "error": ""}

    async def load_skill(self, state: GraphState) -> dict:
        if state.get("error"):
            return {}
        reason = await ServiceObjectFactory.agent_svc().load_skill(
            state["agent"], state["context_id"], state["sub_agent"]
        )
        if reason:
            return {"error": reason}
        return {}

    async def select(self, state: GraphState) -> dict:
        if state.get("error"):
            return {}
        reason = await ServiceObjectFactory.agent_svc().select_and_call(
            state["agent"], state["context_id"], state["sub_agent"], state["tool"]
        )
        if reason:
            return {"error": reason}
        return {}

    async def compress(self, state: GraphState) -> dict:
        if state.get("error"):
            return {}
        reason = await ServiceObjectFactory.agent_svc().compress(
            state["agent"], state["context_id"], state["sub_agent"], state["tool"]
        )
        if reason:
            return {"error": reason}
        return {}

    async def invoke(self, request: InvokeRequest) -> InvokeResponse:
        await ServiceObjectFactory.agent_svc().externalize(self.agent_name, request)
        result = await self.graph().ainvoke(
            {
                "agent": self.agent_name,
                "context_id": request.context_id,
                "tool": request.tool,
                "sub_agent": "",
                "error": "",
            }
        )
        if result.get("error"):
            return InvokeResponse(
                agent=self.agent_name,
                context_id=request.context_id,
                sub_agent=result.get("sub_agent") or "",
                error=result["error"],
            )
        stored = await ServiceObjectFactory.agent_svc().read_parent(self.agent_name, request.context_id)
        return InvokeResponse(
            agent=self.agent_name,
            context_id=request.context_id,
            sub_agent=result.get("sub_agent") or "",
            summary="" if stored is None else stored.summary,
            body={} if stored is None else stored.body,
        )

    async def retrieve(self, context_id: str, sub_agent: str) -> dict | None:
        return await ServiceObjectFactory.agent_svc().retrieve(self.agent_name, context_id, sub_agent)


class OffersAgentWf(_DeskGraph):
    agent_name = "trading-desk-offers"
