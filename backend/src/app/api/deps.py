"""FastAPI dependencies. Singletons live on app.state (created in the lifespan)."""

from typing import Annotated, cast

from fastapi import Depends, Request

from app.core.config import Settings, get_settings
from app.services.items import ItemRepository
from app.services.llm import LLMClient
from app.services.ml import TorchService


def get_llm(request: Request) -> LLMClient:
    return cast(LLMClient, request.app.state.llm)


def get_torch(request: Request) -> TorchService:
    return cast(TorchService, request.app.state.torch)


def get_items(request: Request) -> ItemRepository:
    return cast(ItemRepository, request.app.state.items)


SettingsDep = Annotated[Settings, Depends(get_settings)]
LLMDep = Annotated[LLMClient, Depends(get_llm)]
TorchDep = Annotated[TorchService, Depends(get_torch)]
ItemsDep = Annotated[ItemRepository, Depends(get_items)]
