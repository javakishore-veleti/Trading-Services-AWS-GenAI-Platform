import json

from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

from common.dtos import InvokeRequest, InvokeResponse
from workflows.object_factory import WorkflowObjectFactory


class RetrieveRequest(BaseModel):
    context_id: str
    sub_agent: str


class PlatformRunRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    assistant_id: str
    input: dict = Field(default_factory=dict)
    thread_id: str | None = None


class LangGraphApi:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.router.add_api_route("/agents", self.list_agents, methods=["GET"])
        self.router.add_api_route("/agents/{agent}/invoke", self.invoke, methods=["POST"], response_model=None)
        self.router.add_api_route("/agents/{agent}/retrieve", self.retrieve, methods=["POST"], response_model=None)
        self.router.add_api_route("/runs/wait", self.runs_wait, methods=["POST"], response_model=None)
        self.router.add_api_route("/runs/stream", self.runs_stream, methods=["POST"], response_model=None)

    def list_agents(self) -> dict:
        return {"agents": WorkflowObjectFactory.names()}

    async def invoke(self, agent: str, request: InvokeRequest) -> InvokeResponse | JSONResponse:
        workflow = WorkflowObjectFactory.agent(agent)
        if workflow is None:
            return JSONResponse(status_code=404, content={"error": f"Unknown agent {agent}."})
        return await workflow.invoke(request)

    async def retrieve(self, agent: str, request: RetrieveRequest) -> dict | JSONResponse:
        workflow = WorkflowObjectFactory.agent(agent)
        if workflow is None:
            return JSONResponse(status_code=404, content={"error": f"Unknown agent {agent}."})
        found = await workflow.retrieve(request.context_id, request.sub_agent)
        if found is None:
            return JSONResponse(status_code=404, content={"error": "No stored result for that sub-agent."})
        return found

    async def runs_wait(self, request: PlatformRunRequest) -> dict | JSONResponse:
        content, missing = await self._platform_run(request)
        if missing:
            return JSONResponse(status_code=404, content={"error": content})
        return {"messages": [{"type": "ai", "role": "assistant", "content": content}]}

    async def runs_stream(self, request: PlatformRunRequest) -> StreamingResponse | JSONResponse:
        content, missing = await self._platform_run(request)
        if missing:
            return JSONResponse(status_code=404, content={"error": content})

        def events():
            message = ["messages", [[{"type": "ai", "content": content}, {}]]]
            yield "data: " + json.dumps(message) + "\n\n"
            yield "data: " + json.dumps(["metadata", {"run_id": request.thread_id or request.assistant_id}]) + "\n\n"

        return StreamingResponse(events(), media_type="text/event-stream")

    async def _platform_run(self, request: PlatformRunRequest) -> tuple[str, bool]:
        workflow = WorkflowObjectFactory.agent(request.assistant_id)
        if workflow is None:
            return f"Unknown assistant {request.assistant_id}.", True
        payload = self._tool_payload(request)
        if payload is None:
            return (
                "Send a JSON message with context_id, tool, and arguments. This agent is "
                + request.assistant_id
                + ".",
                False,
            )
        result = await workflow.invoke(
            InvokeRequest(
                context_id=str(payload.get("context_id") or request.thread_id or "langgraph"),
                tool=str(payload["tool"]),
                arguments=payload.get("arguments") if isinstance(payload.get("arguments"), dict) else {},
            )
        )
        if result.error:
            return result.error, False
        text = result.summary or request.assistant_id
        if result.body:
            text = text + "\n" + json.dumps(result.body)
        return text, False

    def _tool_payload(self, request: PlatformRunRequest) -> dict | None:
        messages = request.input.get("messages") if isinstance(request.input, dict) else None
        if not isinstance(messages, list):
            return None
        content = ""
        for message in reversed(messages):
            if not isinstance(message, dict):
                continue
            role = message.get("role") or message.get("type")
            if role not in (None, "human", "user"):
                continue
            raw = message.get("content") or ""
            content = raw if isinstance(raw, str) else json.dumps(raw)
            break
        if not content.strip().startswith("{"):
            return None
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return None
        if not isinstance(parsed, dict) or not parsed.get("tool"):
            return None
        return parsed
