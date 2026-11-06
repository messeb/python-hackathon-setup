from fastapi import APIRouter
from pydantic import BaseModel

from app import __version__
from app.api.deps import LLMDep, SettingsDep, TorchDep

router = APIRouter(prefix="/health", tags=["health"])


class Health(BaseModel):
    status: str
    version: str
    environment: str


class Readiness(Health):
    llm_provider: str
    torch_device: str


@router.get("/live")
async def live(settings: SettingsDep) -> Health:
    """Liveness probe: the process is up."""
    return Health(status="ok", version=__version__, environment=settings.environment)


@router.get("/ready")
async def ready(settings: SettingsDep, llm: LLMDep, torch: TorchDep) -> Readiness:
    """Readiness probe: dependencies are initialised and the app can serve traffic."""
    return Readiness(
        status="ok",
        version=__version__,
        environment=settings.environment,
        llm_provider=llm.provider,
        torch_device=str(torch.device),
    )
