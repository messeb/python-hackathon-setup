"""Any OpenAI-compatible endpoint: OpenAI, Ollama, vLLM, LM Studio, LiteLLM, ..."""

from collections.abc import AsyncIterator
from typing import Any

import openai

from app.core.config import Settings
from app.schemas.llm import ChatMessage, ChatResponse, Usage
from app.services.llm.base import LLMError


class OpenAICompatibleLLM:
    provider = "openai"

    def __init__(self, settings: Settings) -> None:
        self.model = settings.llm_model
        self._settings = settings
        # Local servers (Ollama, vLLM) accept any key; the SDK just requires one.
        key = settings.openai_api_key.get_secret_value() if settings.openai_api_key else "unused"
        self._client = openai.AsyncOpenAI(
            api_key=key,
            base_url=settings.openai_base_url,
            timeout=settings.llm_timeout_seconds,
        )

    def _messages(self, messages: list[ChatMessage]) -> list[Any]:
        system = {"role": "system", "content": self._settings.llm_system_prompt}
        return [system, *(m.model_dump() for m in messages)]

    async def complete(self, messages: list[ChatMessage]) -> ChatResponse:
        try:
            resp = await self._client.chat.completions.create(
                model=self.model,
                messages=self._messages(messages),
                max_completion_tokens=self._settings.llm_max_tokens,
            )
        except openai.APIError as exc:
            raise _translate(exc) from exc
        choice = resp.choices[0]
        return ChatResponse(
            content=choice.message.content or "",
            model=resp.model,
            provider=self.provider,
            stop_reason=choice.finish_reason,
            usage=Usage(
                input_tokens=resp.usage.prompt_tokens if resp.usage else None,
                output_tokens=resp.usage.completion_tokens if resp.usage else None,
            ),
        )

    async def stream(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        try:
            chunks = await self._client.chat.completions.create(
                model=self.model,
                messages=self._messages(messages),
                max_completion_tokens=self._settings.llm_max_tokens,
                stream=True,
            )
            async for chunk in chunks:
                if chunk.choices and (text := chunk.choices[0].delta.content):
                    yield text
        except openai.APIError as exc:
            raise _translate(exc) from exc

    async def aclose(self) -> None:
        await self._client.close()


def _translate(exc: openai.APIError) -> LLMError:
    if isinstance(exc, openai.RateLimitError):
        return LLMError(429, "LLM rate limit exceeded, retry later.")
    if isinstance(exc, openai.APIConnectionError):
        return LLMError(503, "LLM provider unreachable.")
    if isinstance(exc, openai.APIStatusError):
        return LLMError(502, f"LLM provider error ({exc.status_code}).")
    return LLMError(502, "LLM provider error.")
