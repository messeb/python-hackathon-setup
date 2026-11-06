from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import ItemsDep
from app.schemas.items import Item, ItemCreate, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])

NOT_FOUND = "Item not found"


@router.get("")
async def list_items(
    repo: ItemsDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[Item]:
    return repo.list(offset=offset, limit=limit)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_item(data: ItemCreate, repo: ItemsDep) -> Item:
    return repo.create(data)


@router.get("/{item_id}", responses={404: {"description": NOT_FOUND}})
async def get_item(item_id: UUID, repo: ItemsDep) -> Item:
    if (item := repo.get(item_id)) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, NOT_FOUND)
    return item


@router.patch("/{item_id}", responses={404: {"description": NOT_FOUND}})
async def update_item(item_id: UUID, data: ItemUpdate, repo: ItemsDep) -> Item:
    if (item := repo.update(item_id, data)) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, NOT_FOUND)
    return item


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": NOT_FOUND}},
)
async def delete_item(item_id: UUID, repo: ItemsDep) -> None:
    if not repo.delete(item_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, NOT_FOUND)
