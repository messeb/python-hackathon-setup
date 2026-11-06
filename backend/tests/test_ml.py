import pytest
from fastapi.testclient import TestClient


def test_info(client: TestClient) -> None:
    body = client.get("/api/v1/ml/info").json()
    assert body["device"] == "cpu"
    assert body["torch_version"]


def test_similarity(client: TestClient) -> None:
    resp = client.post("/api/v1/ml/similarity", json={"vectors": [[1, 0], [0, 1], [2, 0]]})
    matrix = resp.json()["matrix"]
    assert matrix[0][0] == pytest.approx(1.0)
    assert matrix[0][1] == pytest.approx(0.0)
    assert matrix[0][2] == pytest.approx(1.0)


@pytest.mark.parametrize(
    "vectors",
    [[[1, 2], [1]], [[], []], [[1.0]]],
    ids=["mismatched-dims", "empty", "single-vector"],
)
def test_similarity_rejects_invalid_input(client: TestClient, vectors: list[list[float]]) -> None:
    assert client.post("/api/v1/ml/similarity", json={"vectors": vectors}).status_code == 422


def test_regression_recovers_line(client: TestClient) -> None:
    xs = [float(i) for i in range(20)]
    ys = [3.0 * x - 2.0 for x in xs]
    body = client.post(
        "/api/v1/ml/regression", json={"x": xs, "y": ys, "epochs": 2000, "learning_rate": 0.1}
    ).json()
    assert body["slope"] == pytest.approx(3.0, abs=0.05)
    assert body["intercept"] == pytest.approx(-2.0, abs=0.3)


def test_regression_rejects_length_mismatch(client: TestClient) -> None:
    assert client.post("/api/v1/ml/regression", json={"x": [1, 2], "y": [1]}).status_code == 422
