from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from app.services.ml.torch_service import resolve_device


@pytest.fixture
def spa_client(settings: Settings, tmp_path: Path) -> TestClient:
    static = tmp_path / "static"
    (static / "assets").mkdir(parents=True)
    (static / "index.html").write_text("<html>spa</html>")
    (static / "favicon.ico").write_text("ico")
    (static / "assets" / "app.js").write_text("js")
    return TestClient(create_app(settings.model_copy(update={"static_dir": static})))


def test_spa_routes_fall_back_to_index(spa_client: TestClient) -> None:
    assert spa_client.get("/").text == "<html>spa</html>"
    assert spa_client.get("/some/client/route").text == "<html>spa</html>"
    assert spa_client.get("/favicon.ico").text == "ico"
    assert spa_client.get("/assets/app.js").text == "js"


def test_unknown_api_path_is_404_not_spa(spa_client: TestClient) -> None:
    assert spa_client.get("/api/v1/nope").status_code == 404


def test_path_traversal_is_blocked(spa_client: TestClient) -> None:
    assert spa_client.get("/..%2F..%2Fetc%2Fpasswd").text == "<html>spa</html>"


def test_resolve_device_explicit() -> None:
    assert str(resolve_device("cpu")) == "cpu"
