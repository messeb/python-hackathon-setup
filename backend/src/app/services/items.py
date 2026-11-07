"""In-memory repository. Swap for a database-backed one behind the same interface."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.schemas.items import Item, ItemCreate, ItemUpdate


class ItemRepository:
    def __init__(self) -> None:
        self._items: dict[UUID, Item] = {}

    def list(self, *, offset: int = 0, limit: int = 50) -> list[Item]:
        return list(self._items.values())[offset : offset + limit]

    def get(self, item_id: UUID) -> Item | None:
        return self._items.get(item_id)

    def create(self, data: ItemCreate) -> Item:
        item = Item(id=uuid4(), created_at=datetime.now(UTC), **data.model_dump())
        self._items[item.id] = item
        return item

    def update(self, item_id: UUID, data: ItemUpdate) -> Item | None:
        if (item := self._items.get(item_id)) is None:
            return None
        updated = item.model_copy(update=data.model_dump(exclude_unset=True))
        self._items[item_id] = updated
        return updated

    def delete(self, item_id: UUID) -> bool:
        return self._items.pop(item_id, None) is not None
