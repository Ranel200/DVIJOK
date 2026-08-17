"""Бизнес-логика модуля inventory: остатки и движения товара."""

from decimal import Decimal

from sqlalchemy import select

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.modules.inventory.models import InventoryItem, StockMovement
from app.modules.inventory.repository import InventoryRepository
from app.modules.inventory.schemas import (
    InventoryItemCreate,
    InventoryItemUpdate,
    MovementCreate,
)
from app.modules.orders.models import Order
from app.shared.enums import InventoryCategory, MovementType

# Типы движения, уменьшающие остаток.
_DECREASING = {MovementType.OUT, MovementType.WRITE_OFF}


class InventoryService:
    def __init__(self, repo: InventoryRepository) -> None:
        self.repo = repo
        self.session = repo.session

    async def get(self, item_id: int) -> InventoryItem:
        item = await self.repo.get(item_id)
        if item is None:
            raise NotFoundError("Складская позиция не найдена")
        return item

    async def list_page(
        self,
        *,
        query: str | None,
        category: InventoryCategory | None,
        low_stock: bool,
        limit: int,
        offset: int,
    ) -> tuple[list[InventoryItem], int]:
        return await self.repo.search(
            query=query, category=category, low_stock=low_stock, limit=limit, offset=offset
        )

    async def create(self, data: InventoryItemCreate) -> InventoryItem:
        if await self.repo.get_by_sku(data.sku):
            raise ConflictError("Позиция с таким артикулом уже существует")
        return await self.repo.add(InventoryItem(**data.model_dump()))

    async def update(self, item_id: int, data: InventoryItemUpdate) -> InventoryItem:
        item = await self.get(item_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        return await self.repo.add(item)

    async def delete(self, item_id: int) -> None:
        await self.repo.delete(await self.get(item_id))

    async def register_movement(
        self, item_id: int, data: MovementCreate, user_id: int | None
    ) -> tuple[InventoryItem, StockMovement]:
        item = await self.get(item_id)  # 404, если позиции нет
        if data.order_id is not None:
            result = await self.session.execute(
                select(Order.id).where(
                    Order.id == data.order_id,
                    Order.organization_id == self.repo.organization_id,
                )
            )
            if result.scalar_one_or_none() is None:
                raise NotFoundError("Заказ не найден")
        decreasing = data.movement_type in _DECREASING
        delta = -data.quantity if decreasing else data.quantity

        # Атомарное изменение остатка на уровне БД (без read-modify-write).
        applied = await self.repo.adjust_quantity(item_id, delta, require_nonnegative=decreasing)
        if not applied:
            raise BusinessRuleError(
                f"Недостаточно на складе: остаток {item.quantity}, запрошено {data.quantity}"
            )

        movement = StockMovement(
            inventory_item_id=item.id,
            order_id=data.order_id,
            movement_type=data.movement_type,
            quantity=data.quantity,
            comment=data.comment,
            created_by_id=user_id,
        )
        await self.repo.add_movement(movement)
        await self.session.refresh(item)  # подтянуть актуальный остаток
        return item, movement

    async def write_off_for_order(
        self,
        item_id: int,
        quantity: Decimal,
        order_id: int | None,
        comment: str | None,
        user_id: int | None,
    ) -> tuple[InventoryItem, StockMovement]:
        return await self.register_movement(
            item_id,
            MovementCreate(
                movement_type=MovementType.WRITE_OFF,
                quantity=quantity,
                order_id=order_id,
                comment=comment,
            ),
            user_id,
        )

    async def list_movements(
        self, item_id: int, *, limit: int, offset: int
    ) -> tuple[list[StockMovement], int]:
        await self.get(item_id)  # 404 если позиции нет
        return await self.repo.list_movements(item_id, limit=limit, offset=offset)
