from fastapi import APIRouter

from app.api.deps import TorchDep
from app.schemas.ml import (
    RegressionRequest,
    RegressionResponse,
    SimilarityRequest,
    SimilarityResponse,
    TorchInfo,
)

router = APIRouter(prefix="/ml", tags=["ml"])

# Routes below are deliberately sync (`def`): FastAPI runs them in a threadpool so
# CPU-bound tensor work never blocks the event loop.


@router.get("/info")
def torch_info(torch: TorchDep) -> TorchInfo:
    return torch.info()


@router.post("/similarity")
def similarity(request: SimilarityRequest, torch: TorchDep) -> SimilarityResponse:
    """Pairwise cosine similarity matrix of the given vectors."""
    return SimilarityResponse(matrix=torch.cosine_similarity(request.vectors))


@router.post("/regression")
def regression(request: RegressionRequest, torch: TorchDep) -> RegressionResponse:
    """Fit a linear model with PyTorch autograd and return its parameters."""
    return torch.fit_linear_regression(
        request.x, request.y, epochs=request.epochs, learning_rate=request.learning_rate
    )
