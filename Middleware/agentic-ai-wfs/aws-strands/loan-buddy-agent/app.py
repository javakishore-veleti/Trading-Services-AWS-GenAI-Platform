import json
import os
import secrets
from contextlib import asynccontextmanager
from io import BytesIO
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image
from pydantic import BaseModel, ConfigDict, Field
from strands import Agent, tool
from strands.models.litellm import LiteLLMModel

IMAGE_DIR = Path(__file__).resolve().parents[1] / ".run" / "loan-images"


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

SYSTEM_PROMPT = """You are a helpful assistant for credit underwriting.

A credit application image is stored on this computer. You do not receive the image bytes.
Call application_image with the image_id. That tool reports whether the file is present and how large it is.
This local stack has no document-extraction service, so you cannot read the text inside the image.
Say that plainly, then list what a reviewer would still need before an APPROVED, REJECTED, or CONDITIONAL decision.
Do not invent applicant names, income, or addresses.
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


@tool
def application_image(image_id: str) -> str:
    """Look up a stored credit-application image by id. Returns whether the file exists and its size in bytes."""
    path = IMAGE_DIR / f"{image_id}.jpg"
    if not path.is_file():
        return f"No application image is stored for {image_id}."
    return (
        f"Application image {image_id} is stored locally. "
        f"Size {path.stat().st_size} bytes. The text inside the image is not available."
    )


def store_jpeg(image_bytes: bytes, image_id: str) -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    buffer = BytesIO()
    Image.open(BytesIO(image_bytes)).convert("RGB").save(buffer, format="JPEG", quality=90)
    (IMAGE_DIR / f"{image_id}.jpg").write_bytes(buffer.getvalue())


class LoanBuddyHost:
    def __init__(self) -> None:
        self._name = "strands-loan-buddy-agent"
        self._port = 8302
        self._agent: Agent | None = None

    def build(self) -> FastAPI:
        host = self

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            host._agent = Agent(
                model=litellm_model(),
                system_prompt=SYSTEM_PROMPT,
                tools=[application_image],
            )
            yield

        app = FastAPI(title=self._name, lifespan=lifespan)
        app.add_api_route("/health", self.health, methods=["GET"])
        app.add_api_route(
            "/api/process_credit_application_with_upload",
            self.process_upload,
            methods=["POST"],
        )
        app.add_api_route("/runs/wait", self.runs_wait, methods=["POST"])
        app.add_api_route("/runs/stream", self.runs_stream, methods=["POST"])
        return app

    def health(self) -> dict[str, str]:
        return {"status": "ok", "service": self._name}

    def answer(self, text: str) -> str:
        if self._agent is None:
            return "The loan agent is not ready."
        return str(self._agent(text))

    async def runs_wait(self, request: PlatformRunRequest) -> dict[str, list]:
        return platform_messages(self.answer(last_user_text(request)))

    async def runs_stream(self, request: PlatformRunRequest) -> StreamingResponse:
        content = self.answer(last_user_text(request))

        def events():
            message = ["messages", [[{"type": "ai", "content": content}, {}]]]
            yield "data: " + json.dumps(message) + "\n\n"
            yield "data: " + json.dumps(["metadata", {"run_id": request.thread_id or self._name}]) + "\n\n"

        return StreamingResponse(events(), media_type="text/event-stream")

    async def process_upload(self, image_file: UploadFile = File(...)) -> dict[str, str]:
        if self._agent is None:
            return {"status": "ERROR", "message": "The loan agent is not ready."}
        image_bytes = await image_file.read()
        image_id = secrets.token_hex(32)
        try:
            store_jpeg(image_bytes, image_id)
        except Exception as exc:
            return {"status": "ERROR", "message": f"Could not store the image: {exc}"}
        prompt = (
            "Process this credit application.\n\n"
            f"Image_Id: {image_id}\n\n"
            "Call application_image with that id. "
            "Then say what is still missing before a credit decision."
        )
        result = self.answer(prompt)
        return {
            "status": "COMPLETED",
            "image_id": image_id,
            "credit_assessment": str(result),
        }

    def run(self) -> None:
        uvicorn.run(self.build(), host="127.0.0.1", port=self._port)


if __name__ == "__main__":
    LoanBuddyHost().run()
