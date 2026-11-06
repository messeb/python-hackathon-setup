from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        _env_file=None,  # never read a developer's .env in tests
        environment="test",
        llm_provider="fake",
        torch_device="cpu",
        static_dir=tmp_path / "no-frontend",
    )


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings)) as c:
        yield c


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
