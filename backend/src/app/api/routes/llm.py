from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.sse import EventSourceResponse, ServerSentEvent

from app.api.deps import LLMDep
from app.schemas.llm import ChatRequest, ChatResponse, ProviderInfo
from app.services.llm import LLMError

router = APIRouter(prefix="/llm", tags=["llm"])


@router.get("/info")
async def provider_info(llm: LLMDep) -> ProviderInfo:
    return ProviderInfo(provider=llm.provider, model=llm.model)


@router.post("/chat")
async def chat(request: ChatRequest, llm: LLMDep) -> ChatResponse:
    """Single request/response completion."""
    return await llm.complete(request.messages)


@router.post("/chat/stream", response_class=EventSourceResponse)
async def chat_stream(request: ChatRequest, llm: LLMDep) -> AsyncIterator[ServerSentEvent]:
    """Token stream as Server-Sent Events: `delta`* then `done` (or `error`)."""
    try:
        async for text in llm.stream(request.messages):
            yield ServerSentEvent(event="delta", data={"text": text})
    except LLMError as exc:
        yield ServerSentEvent(event="error", data={"status": exc.status_code, "detail": exc.detail})
        return
    yield ServerSentEvent(event="done", data={"provider": llm.provider, "model": llm.model})
