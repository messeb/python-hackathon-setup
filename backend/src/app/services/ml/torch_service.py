"""PyTorch workloads. CPU-bound: call from sync routes so FastAPI uses its threadpool."""

import torch
from torch import nn

from app.schemas.ml import RegressionResponse, TorchInfo


def resolve_device(preference: str) -> torch.device:
    if preference != "auto":
        return torch.device(preference)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


class TorchService:
    def __init__(self, device: str = "auto", seed: int = 42) -> None:
        self.device = resolve_device(device)
        self._seed = seed

    def info(self) -> TorchInfo:
        return TorchInfo(
            torch_version=torch.__version__,
            device=str(self.device),
            cuda_available=torch.cuda.is_available(),
            mps_available=torch.backends.mps.is_available(),
            threads=torch.get_num_threads(),
        )

    @torch.inference_mode()
    def cosine_similarity(self, vectors: list[list[float]]) -> list[list[float]]:
        t = torch.tensor(vectors, dtype=torch.float32, device=self.device)
        t = nn.functional.normalize(t, dim=1)
        result: list[list[float]] = (t @ t.T).clamp(-1.0, 1.0).cpu().tolist()
        return result

    def fit_linear_regression(
        self, x: list[float], y: list[float], *, epochs: int, learning_rate: float
    ) -> RegressionResponse:
        """Fit y = slope * x + intercept with gradient descent (demonstrates autograd)."""
        generator = torch.Generator().manual_seed(self._seed)
        xs = torch.tensor(x, dtype=torch.float32).unsqueeze(1)
        ys = torch.tensor(y, dtype=torch.float32).unsqueeze(1)
        # Standardise x for stable optimisation, then map parameters back.
        mean, std = xs.mean(), xs.std().clamp_min(1e-8)
        xs_n = ((xs - mean) / std).to(self.device)
        ys = ys.to(self.device)

        model = nn.Linear(1, 1).to(self.device)
        with torch.no_grad():
            model.weight.copy_(torch.randn(1, 1, generator=generator))
            model.bias.zero_()
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        loss_fn = nn.MSELoss()

        loss = torch.tensor(0.0)
        for _ in range(epochs):
            optimizer.zero_grad()
            loss = loss_fn(model(xs_n), ys)
            loss.backward()
            optimizer.step()

        w, b = model.weight.item(), model.bias.item()
        slope = w / std.item()
        return RegressionResponse(
            slope=slope,
            intercept=b - slope * mean.item(),
            final_loss=loss.item(),
            epochs=epochs,
        )
