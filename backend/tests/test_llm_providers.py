"""Provider adapters tested against stubbed SDK clients (no network)."""

from collections.abc import AsyncIterator
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import anthropic
import openai
import pytest

from app.core.config import Settings
from app.schemas.llm import ChatMessage
from app.services.llm import LLMError
from app.services.llm.anthropic_client import FALLBACK_BETA, AnthropicLLM
from app.services.llm.openai_client import OpenAICompatibleLLM

pytestmark = pytest.mark.anyio
MESSAGES = [ChatMessage(role="user", content="hi")]


def _settings(**overrides: Any) -> Settings:
    return Settings(_env_file=None, anthropic_api_key="sk-test", **overrides)


async def _aiter(*items: Any) -> AsyncIterator[Any]:
    for item in items:
        yield item


def _status_error(cls: type[Exception], code: int) -> Exception:
    return cls("boom", response=MagicMock(status_code=code), body=None)  # type: ignore[call-arg]


# --- Anthropic -------------------------------------------------------------------


def _claude_message(stop_reason: str = "end_turn") -> SimpleNamespace:
    return SimpleNamespace(
        content=[SimpleNamespace(type="thinking"), SimpleNamespace(type="text", text="Hello")],
        model="claude-opus-5-5",
        stop_reason=stop_reason,
        usage=SimpleNamespace(input_tokens=3, output_tokens=1),
    )


class _StreamCtx:
    def __init__(self, chunks: list[str], final: SimpleNamespace) -> None:
        self.text_stream = _aiter(*chunks)
        self._final = final

    async def __aenter__(self) -> "_StreamCtx":
        return self

    async def __aexit__(self, *exc: object) -> None:
        return None

    async def get_final_message(self) -> SimpleNamespace:
        return self._final


def _claude(settings: Settings | None = None) -> tuple[AnthropicLLM, MagicMock]:
    llm = AnthropicLLM(settings or _settings())
    sdk = MagicMock()
    llm._client = sdk
    return llm, sdk


async def test_anthropic_complete_sends_fallback_and_effort() -> None:
    llm, sdk = _claude()
    sdk.beta.messages.create = AsyncMock(return_value=_claude_message())
    resp = await llm.complete(MESSAGES)
    assert resp.content == "Hello"
    assert resp.usage.output_tokens == 1
    kwargs = sdk.beta.messages.create.call_args.kwargs
    assert kwargs["betas"] == [FALLBACK_BETA]
    assert kwargs["fallbacks"] == "default"
    assert kwargs["output_config"] == {"effort": "medium"}


async def test_anthropic_fallback_can_be_disabled() -> None:
    llm, sdk = _claude(_settings(llm_refusal_fallback=False))
    sdk.beta.messages.create = AsyncMock(return_value=_claude_message())
    await llm.complete(MESSAGES)
    assert "fallbacks" not in sdk.beta.messages.create.call_args.kwargs


async def test_anthropic_refusal_maps_to_422() -> None:
    llm, sdk = _claude()
    sdk.beta.messages.create = AsyncMock(return_value=_claude_message("refusal"))
    with pytest.raises(LLMError) as err:
        await llm.complete(MESSAGES)
    assert err.value.status_code == 422


async def test_anthropic_stream() -> None:
    llm, sdk = _claude()
    sdk.beta.messages.stream = MagicMock(return_value=_StreamCtx(["He", "llo"], _claude_message()))
    assert [t async for t in llm.stream(MESSAGES)] == ["He", "llo"]


@pytest.mark.parametrize(
    ("exc", "status"),
    [
        (_status_error(anthropic.RateLimitError, 429), 429),
        (_status_error(anthropic.InternalServerError, 500), 502),
        (anthropic.APIConnectionError(request=MagicMock()), 503),
    ],
)
async def test_anthropic_errors_translated(exc: Exception, status: int) -> None:
    llm, sdk = _claude()
    sdk.beta.messages.create = AsyncMock(side_effect=exc)
    sdk.beta.messages.stream = MagicMock(side_effect=exc)
    with pytest.raises(LLMError) as err:
        await llm.complete(MESSAGES)
    assert err.value.status_code == status
    with pytest.raises(LLMError):
        _ = [t async for t in llm.stream(MESSAGES)]


# --- OpenAI-compatible ---------------------------------------------------------


def _oai() -> tuple[OpenAICompatibleLLM, MagicMock]:
    llm = OpenAICompatibleLLM(_settings(llm_provider="openai", llm_model="llama3.2"))
    sdk = MagicMock()
    llm._client = sdk
    return llm, sdk


async def test_openai_complete_prepends_system_prompt() -> None:
    llm, sdk = _oai()
    sdk.chat.completions.create = AsyncMock(
        return_value=SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Hey"), finish_reason="stop")],
            model="llama3.2",
            usage=SimpleNamespace(prompt_tokens=5, completion_tokens=2),
        )
    )
    resp = await llm.complete(MESSAGES)
    assert resp.content == "Hey"
    assert resp.usage.input_tokens == 5
    sent = sdk.chat.completions.create.call_args.kwargs["messages"]
    assert sent[0]["role"] == "system"


async def test_openai_stream_skips_empty_chunks() -> None:
    llm, sdk = _oai()

    def chunk(text: str | None) -> SimpleNamespace:
        return SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=text))])

    sdk.chat.completions.create = AsyncMock(
        return_value=_aiter(chunk("A"), chunk(None), SimpleNamespace(choices=[]), chunk("B"))
    )
    assert [t async for t in llm.stream(MESSAGES)] == ["A", "B"]


@pytest.mark.parametrize(
    ("exc", "status"),
    [
        (_status_error(openai.RateLimitError, 429), 429),
        (_status_error(openai.InternalServerError, 500), 502),
        (openai.APIConnectionError(request=MagicMock()), 503),
    ],
)
async def test_openai_errors_translated(exc: Exception, status: int) -> None:
    llm, sdk = _oai()
    sdk.chat.completions.create = AsyncMock(side_effect=exc)
    with pytest.raises(LLMError) as err:
        await llm.complete(MESSAGES)
    assert err.value.status_code == status
    with pytest.raises(LLMError):
        _ = [t async for t in llm.stream(MESSAGES)]
