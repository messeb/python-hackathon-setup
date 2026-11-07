from fastapi import APIRouter

from app.api.routes import items, llm, ml

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(items.router)
api_router.include_router(llm.router)
api_router.include_router(ml.router)
