"""Claude via the official Anthropic SDK."""

from collections.abc import AsyncIterator
from typing import Any

import anthropic
from anthropic.types.beta import BetaMessage

from app.core.config import Settings
from app.schemas.llm import ChatMessage, ChatResponse, Usage
from app.services.llm.base import LLMError

# Server-side refusal fallback: on a policy decline the API re-runs the request on a
# suitable fallback model inside the same call ("default" routes by refusal category).
FALLBACK_BETA = "server-side-fallback-2026-07-01"


class AnthropicLLM:
    provider = "anthropic"

    def __init__(self, settings: Settings) -> None:
        if settings.anthropic_api_key is None:
            raise ValueError("APP_ANTHROPIC_API_KEY is required for llm_provider=anthropic")
        self.model = settings.llm_model
        self._settings = settings
        self._client = anthropic.AsyncAnthropic(
            api_key=settings.anthropic_api_key.get_secret_value(),
            timeout=settings.llm_timeout_seconds,
        )

    def _params(self, messages: list[ChatMessage]) -> dict[str, Any]:
        params: dict[str, Any] = {
            "model": self.model,
            "max_tokens": self._settings.llm_max_tokens,
            "system": self._settings.llm_system_prompt,
            "messages": [m.model_dump() for m in messages],
            "output_config": {"effort": self._settings.llm_effort},
        }
        if self._settings.llm_refusal_fallback:
            params["betas"] = [FALLBACK_BETA]
            params["fallbacks"] = "default"
        return params

    @staticmethod
    def _check_refusal(message: BetaMessage) -> None:
        if message.stop_reason == "refusal":
            raise LLMError(422, "The model declined to answer this request.")

    async def complete(self, messages: list[ChatMessage]) -> ChatResponse:
        try:
            message = await self._client.beta.messages.create(**self._params(messages))
        except anthropic.APIError as exc:
            raise _translate(exc) from exc
        self._check_refusal(message)
        return ChatResponse(
            content="".join(b.text for b in message.content if b.type == "text"),
            model=message.model,
            provider=self.provider,
            stop_reason=message.stop_reason,
            usage=Usage(
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
            ),
        )

    async def stream(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        try:
            async with self._client.beta.messages.stream(**self._params(messages)) as stream:
                async for text in stream.text_stream:
                    yield text
                self._check_refusal(await stream.get_final_message())
        except anthropic.APIError as exc:
            raise _translate(exc) from exc

    async def aclose(self) -> None:
        await self._client.close()


def _translate(exc: anthropic.APIError) -> LLMError:
    # Most specific first: retryable (429/5xx/network) vs. client errors.
    if isinstance(exc, anthropic.RateLimitError):
        return LLMError(429, "LLM rate limit exceeded, retry later.")
    if isinstance(exc, anthropic.APIConnectionError):
        return LLMError(503, "LLM provider unreachable.")
    if isinstance(exc, anthropic.APIStatusError):
        return LLMError(502, f"LLM provider error ({exc.status_code}).")
    return LLMError(502, "LLM provider error.")
