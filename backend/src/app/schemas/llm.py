from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=32_000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=50)


class Usage(BaseModel):
    input_tokens: int | None = None
    output_tokens: int | None = None


class ChatResponse(BaseModel):
    content: str
    model: str
    provider: str
    stop_reason: str | None = None
    usage: Usage = Field(default_factory=Usage)


class ProviderInfo(BaseModel):
    provider: str
    model: str
