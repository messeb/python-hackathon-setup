from fastapi.testclient import TestClient


def test_live(client: TestClient) -> None:
    resp = client.get("/health/live")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_ready_reports_dependencies(client: TestClient) -> None:
    body = client.get("/health/ready").json()
    assert body["llm_provider"] == "fake"
    assert body["torch_device"] == "cpu"


def test_openapi_is_served(client: TestClient) -> None:
    assert client.get("/api/openapi.json").status_code == 200
