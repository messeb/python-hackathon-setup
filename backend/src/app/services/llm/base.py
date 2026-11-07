"""Provider-agnostic LLM interface. Routes depend on this, never on an SDK."""

from collections.abc import AsyncIterator
from typing import Protocol

from app.schemas.llm import ChatMessage, ChatResponse


class LLMError(Exception):
    """Provider failure translated to an HTTP-friendly status code."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class LLMClient(Protocol):
    provider: str
    model: str

    async def complete(self, messages: list[ChatMessage]) -> ChatResponse: ...

    def stream(self, messages: list[ChatMessage]) -> AsyncIterator[str]: ...

    async def aclose(self) -> None: ...
