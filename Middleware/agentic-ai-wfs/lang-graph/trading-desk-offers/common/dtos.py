from pydantic import BaseModel, Field


class InvokeRequest(BaseModel):
    context_id: str
    tool: str
    arguments: dict = Field(default_factory=dict)


class InvokeResponse(BaseModel):
    agent: str
    context_id: str
    sub_agent: str = ""
    summary: str = ""
    body: dict = Field(default_factory=dict)
    error: str | None = None


class StoredSlice(BaseModel):
    summary: str
    body: dict = Field(default_factory=dict)
