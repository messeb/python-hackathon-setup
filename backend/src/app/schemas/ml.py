from typing import Self

from pydantic import BaseModel, Field, model_validator


class TorchInfo(BaseModel):
    torch_version: str
    device: str
    cuda_available: bool
    mps_available: bool
    threads: int


class SimilarityRequest(BaseModel):
    vectors: list[list[float]] = Field(min_length=2, max_length=256)

    @model_validator(mode="after")
    def _same_dim(self) -> Self:
        dims = {len(v) for v in self.vectors}
        if len(dims) != 1 or 0 in dims:
            raise ValueError("all vectors must be non-empty and share one dimension")
        if dims.pop() > 4096:
            raise ValueError("vector dimension must be <= 4096")
        return self


class SimilarityResponse(BaseModel):
    matrix: list[list[float]]


class RegressionRequest(BaseModel):
    x: list[float] = Field(min_length=2, max_length=10_000)
    y: list[float] = Field(min_length=2, max_length=10_000)
    epochs: int = Field(default=500, ge=1, le=5_000)
    learning_rate: float = Field(default=0.05, gt=0, le=1)

    @model_validator(mode="after")
    def _same_len(self) -> Self:
        if len(self.x) != len(self.y):
            raise ValueError("x and y must have the same length")
        return self


class RegressionResponse(BaseModel):
    slope: float
    intercept: float
    final_loss: float
    epochs: int
