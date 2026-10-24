import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai.like import OpenAILike
from agno.tools.calculator import CalculatorTools
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

DB_FILE = str(Path(__file__).resolve().parents[1] / ".run" / "calculator.db")

SYSTEM_PROMPT = """
You are a helpful calculator assistant that can perform basic arithmetic operations.

You have access to calculator tools for addition, subtraction, multiplication, and division.
When asked to perform calculations, use the calculator tool rather than calculating the result yourself.
Explain the calculation and show the result clearly.
"""


class PromptRequest(BaseModel):
    prompt: str


class PlatformRunRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    assistant_id: str = ""
    input: dict = Field(default_factory=dict)
    thread_id: str | None = None


def last_user_text(request: PlatformRunRequest) -> str:
    messages = request.input.get("messages") if isinstance(request.input, dict) else None
    if not isinstance(messages, list):
        return ""
    for message in reversed(messages):
        if not isinstance(message, dict):
            continue
        role = message.get("role") or message.get("type")
        if role not in (None, "human", "user"):
            continue
        raw = message.get("content") or ""
        return raw if isinstance(raw, str) else json.dumps(raw)
    return ""


def platform_messages(content: str) -> dict[str, list]:
    return {"messages": [{"type": "ai", "role": "assistant", "content": content}]}


def litellm_model() -> OpenAILike:
    base = os.environ.get("LITELLM_BASE_URL", "http://127.0.0.1:4000").rstrip("/")
    if not base.endswith("/v1"):
        base = f"{base}/v1"
    return OpenAILike(
        base_url=base,
        api_key=os.environ.get("LITELLM_API_KEY", ""),
        id=os.environ.get("LITELLM_MODEL_NAME", "deepseek-r1-8b-ollama"),
    )


class CalculatorHost:
    def __init__(self) -> None:
        self._name = "agno-calculator-agent"
        self._port = 8401
        self._agent: Agent | None = None

    def build(self) -> FastAPI:
        host = self

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            Path(DB_FILE).parent.mkdir(parents=True, exist_ok=True)
            model = litellm_model()
            db = SqliteDb(db_file=DB_FILE)
            host._agent = Agent(
                model=model,
                system_message=SYSTEM_PROMPT,
                tools=[CalculatorTools()],
                db=db,
                add_history_to_context=True,
                num_history_runs=3,
                telemetry=False,
            )
            yield

        app = FastAPI(title=self._name, lifespan=lifespan)
        app.add_api_route("/health", self.health, methods=["GET"])
        app.add_api_route("/", self.prompt, methods=["POST"])
        app.add_api_route("/runs/wait", self.runs_wait, methods=["POST"])
        app.add_api_route("/runs/stream", self.runs_stream, methods=["POST"])
        return app

    def health(self) -> dict[str, str]:
        return {"status": "ok", "service": self._name}

    async def answer(self, text: str) -> str:
        if self._agent is None:
            return "The calculator agent is not ready."
        response = await self._agent.arun(text, user_id="local", stream=False)
        return str(response.content)

    async def prompt(self, request: PromptRequest) -> str:
        return await self.answer(request.prompt)

    async def runs_wait(self, request: PlatformRunRequest) -> dict[str, list]:
        return platform_messages(await self.answer(last_user_text(request)))

    async def runs_stream(self, request: PlatformRunRequest) -> StreamingResponse:
        content = await self.answer(last_user_text(request))

        def events():
            message = ["messages", [[{"type": "ai", "content": content}, {}]]]
            yield "data: " + json.dumps(message) + "\n\n"
            yield "data: " + json.dumps(["metadata", {"run_id": request.thread_id or self._name}]) + "\n\n"

        return StreamingResponse(events(), media_type="text/event-stream")

    def run(self) -> None:
        uvicorn.run(self.build(), host="127.0.0.1", port=self._port)


if __name__ == "__main__":
    CalculatorHost().run()
