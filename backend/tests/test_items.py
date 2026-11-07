from uuid import uuid4

from fastapi.testclient import TestClient


def test_item_crud_roundtrip(client: TestClient) -> None:
    created = client.post("/api/v1/items", json={"name": "GPU", "price": 999.0})
    assert created.status_code == 201
    item_id = created.json()["id"]

    assert client.get(f"/api/v1/items/{item_id}").json()["name"] == "GPU"
    assert len(client.get("/api/v1/items").json()) == 1

    patched = client.patch(f"/api/v1/items/{item_id}", json={"price": 899.0})
    assert patched.json()["price"] == 899.0
    assert patched.json()["name"] == "GPU"

    assert client.delete(f"/api/v1/items/{item_id}").status_code == 204
    assert client.get(f"/api/v1/items/{item_id}").status_code == 404


def test_unknown_item_returns_404(client: TestClient) -> None:
    missing = uuid4()
    assert client.get(f"/api/v1/items/{missing}").status_code == 404
    assert client.patch(f"/api/v1/items/{missing}", json={"price": 1}).status_code == 404
    assert client.delete(f"/api/v1/items/{missing}").status_code == 404


def test_validation_rejects_negative_price(client: TestClient) -> None:
    assert client.post("/api/v1/items", json={"name": "x", "price": -1}).status_code == 422
