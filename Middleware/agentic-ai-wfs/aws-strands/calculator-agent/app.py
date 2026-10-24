import json
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from strands import Agent, tool
from strands.models.litellm import LiteLLMModel


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


@tool
def add(x: float, y: float) -> float:
    """Add two numbers together."""
    return x + y


@tool
def subtract(x: float, y: float) -> float:
    """Subtract y from x."""
    return x - y


@tool
def multiply(x: float, y: float) -> float:
    """Multiply two numbers together."""
    return x * y


@tool
def divide(x: float, y: float) -> str:
    """Divide x by y."""
    if y == 0:
        return "Cannot divide by zero."
    return str(x / y)


SYSTEM_PROMPT = """
You are a helpful calculator assistant that can perform basic arithmetic operations.

You have access to the following calculator tools:
- add: Add two numbers together
- subtract: Subtract one number from another
- multiply: Multiply two numbers together
- divide: Divide one number by another

When asked to perform calculations, use the appropriate tool rather than calculating the result yourself.
Explain the calculation and show the result clearly.
"""


def litellm_model() -> LiteLLMModel:
    base = os.environ.get("LITELLM_BASE_URL", "http://127.0.0.1:4000").rstrip("/")
    if not base.endswith("/v1"):
        base = f"{base}/v1"
    model_name = os.environ.get("LITELLM_MODEL_NAME", "deepseek-r1-8b-ollama")
    return LiteLLMModel(
        client_args={
            "base_url": base,
            "api_key": os.environ.get("LITELLM_API_KEY", ""),
        },
        model_id=f"openai/{model_name}",
    )


class CalculatorHost:
    def __init__(self) -> None:
        self._name = "strands-calculator-agent"
        self._port = 8301
        self._agent: Agent | None = None

    def build(self) -> FastAPI:
        host = self

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            host._agent = Agent(
                model=litellm_model(),
                system_prompt=SYSTEM_PROMPT,
                tools=[add, subtract, multiply, divide],
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

    def answer(self, text: str) -> str:
        if self._agent is None:
            return "The calculator agent is not ready."
        return str(self._agent(text))

    async def prompt(self, request: PromptRequest) -> str:
        return self.answer(request.prompt)

    async def runs_wait(self, request: PlatformRunRequest) -> dict[str, list]:
        return platform_messages(self.answer(last_user_text(request)))

    async def runs_stream(self, request: PlatformRunRequest) -> StreamingResponse:
        content = self.answer(last_user_text(request))

        def events():
            message = ["messages", [[{"type": "ai", "content": content}, {}]]]
            yield "data: " + json.dumps(message) + "\n\n"
            yield "data: " + json.dumps(["metadata", {"run_id": request.thread_id or self._name}]) + "\n\n"

        return StreamingResponse(events(), media_type="text/event-stream")

    def run(self) -> None:
        uvicorn.run(self.build(), host="127.0.0.1", port=self._port)


if __name__ == "__main__":
    CalculatorHost().run()
