"""Deterministic offline provider: lets the app, tests and CI run without API keys."""

import asyncio
from collections.abc import AsyncIterator

from app.schemas.llm import ChatMessage, ChatResponse


class FakeLLM:
    provider = "fake"
    model = "fake-echo"

    def __init__(self, delay_seconds: float = 0.0) -> None:
        self._delay = delay_seconds

    @staticmethod
    def _reply(messages: list[ChatMessage]) -> str:
        return f"Echo: {messages[-1].content}"

    async def complete(self, messages: list[ChatMessage]) -> ChatResponse:
        return ChatResponse(
            content=self._reply(messages),
            model=self.model,
            provider=self.provider,
            stop_reason="end_turn",
        )

    async def stream(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        for i, word in enumerate(self._reply(messages).split(" ")):
            await asyncio.sleep(self._delay)
            yield word if i == 0 else f" {word}"

    async def aclose(self) -> None:
        return None
