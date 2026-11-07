import json
from collections.abc import AsyncIterator

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.schemas.llm import ChatMessage, ChatResponse
from app.services.llm import LLMError, create_llm_client

CHAT = {"messages": [{"role": "user", "content": "hello world"}]}


def _sse_events(raw: str) -> list[tuple[str, dict[str, object]]]:
    events = []
    for block in raw.strip().split("\n\n"):
        fields = dict(line.split(": ", 1) for line in block.splitlines() if ": " in line)
        events.append((fields["event"], json.loads(fields["data"])))
    return events


def test_info(client: TestClient) -> None:
    assert client.get("/api/v1/llm/info").json() == {"provider": "fake", "model": "fake-echo"}


def test_chat(client: TestClient) -> None:
    body = client.post("/api/v1/llm/chat", json=CHAT).json()
    assert body["content"] == "Echo: hello world"
    assert body["provider"] == "fake"


def test_chat_stream(client: TestClient) -> None:
    resp = client.post("/api/v1/llm/chat/stream", json=CHAT)
    assert resp.headers["content-type"].startswith("text/event-stream")
    events = _sse_events(resp.text)
    text = "".join(str(data["text"]) for name, data in events if name == "delta")
    assert text == "Echo: hello world"
    assert events[-1][0] == "done"


def test_chat_rejects_empty_messages(client: TestClient) -> None:
    assert client.post("/api/v1/llm/chat", json={"messages": []}).status_code == 422


class FailingLLM:
    provider = "failing"
    model = "none"

    async def complete(self, messages: list[ChatMessage]) -> ChatResponse:
        raise LLMError(429, "slow down")

    async def stream(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        yield "partial"
        raise LLMError(503, "gone")

    async def aclose(self) -> None:
        return None


def test_provider_errors_are_translated(client: TestClient) -> None:
    client.app.state.llm = FailingLLM()  # type: ignore[attr-defined]
    resp = client.post("/api/v1/llm/chat", json=CHAT)
    assert resp.status_code == 429
    assert resp.json() == {"detail": "slow down"}

    events = _sse_events(client.post("/api/v1/llm/chat/stream", json=CHAT).text)
    assert events[0] == ("delta", {"text": "partial"})
    assert events[-1] == ("error", {"status": 503, "detail": "gone"})


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("overrides", "provider"),
    [
        ({"llm_provider": "anthropic", "anthropic_api_key": "sk-test"}, "anthropic"),
        ({"llm_provider": "openai", "openai_base_url": "http://localhost:11434/v1"}, "openai"),
        ({"llm_provider": "fake"}, "fake"),
    ],
)
async def test_factory_builds_each_provider(overrides: dict[str, str], provider: str) -> None:
    client = create_llm_client(Settings(_env_file=None, **overrides))  # type: ignore[arg-type]
    assert client.provider == provider
    await client.aclose()


def test_anthropic_requires_key() -> None:
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        create_llm_client(Settings(_env_file=None, llm_provider="anthropic"))
