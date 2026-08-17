"""Репозиторий модуля inventory."""

from decimal import Decimal

from sqlalchemy import and_, func, select, update

from app.modules.inventory.models import InventoryItem, StockMovement
from app.shared.base_repository import BaseRepository
from app.shared.enums import InventoryCategory


class InventoryRepository(BaseRepository[InventoryItem]):
    model = InventoryItem

    async def get_by_sku(self, sku: str) -> InventoryItem | None:
        result = await self.session.execute(
            select(InventoryItem).where(
                InventoryItem.sku == sku, InventoryItem.organization_id == self.organization_id
            )
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        *,
        query: str | None = None,
        category: InventoryCategory | None = None,
        low_stock: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[InventoryItem], int]:
        conditions = [InventoryItem.organization_id == self.organization_id]
        if category is not None:
            conditions.append(InventoryItem.category == category)
        if low_stock:
            conditions.append(InventoryItem.quantity <= InventoryItem.min_quantity)
        if query:
            like = f"%{query}%"
            conditions.append(
                func.lower(InventoryItem.name).like(func.lower(like))
                | func.lower(InventoryItem.sku).like(func.lower(like))
            )

        base = select(InventoryItem)
        if conditions:
            base = base.where(and_(*conditions))

        total = int(
            (
                await self.session.execute(select(func.count()).select_from(base.subquery()))
            ).scalar_one()
        )
        items = list(
            (
                await self.session.execute(
                    base.order_by(InventoryItem.name).limit(limit).offset(offset)
                )
            )
            .scalars()
            .all()
        )
        return items, total

    async def adjust_quantity(
        self, item_id: int, delta: Decimal, *, require_nonnegative: bool
    ) -> bool:
        """Атомарно меняет остаток на delta (может быть отрицательным).

        При require_nonnegative=True изменение применяется только если итог >= 0
        (условие в WHERE). Возвращает True, если строка обновлена (позиция есть и
        условие выполнено) — это устраняет race condition read-modify-write.
        """
        stmt = update(InventoryItem).where(
            InventoryItem.id == item_id, InventoryItem.organization_id == self.organization_id
        )
        if require_nonnegative:
            stmt = stmt.where(InventoryItem.quantity + delta >= 0)
        stmt = stmt.values(quantity=InventoryItem.quantity + delta)
        result = await self.session.execute(stmt)
        return result.rowcount == 1

    async def add_movement(self, movement: StockMovement) -> StockMovement:
        movement.organization_id = self.organization_id  # type: ignore[assignment]
        self.session.add(movement)
        await self.session.flush()
        await self.session.refresh(movement)
        return movement

    async def list_movements(
        self, item_id: int, *, limit: int = 50, offset: int = 0
    ) -> tuple[list[StockMovement], int]:
        base = select(StockMovement).where(
            StockMovement.inventory_item_id == item_id,
            StockMovement.organization_id == self.organization_id,
        )
        total = int(
            (
                await self.session.execute(select(func.count()).select_from(base.subquery()))
            ).scalar_one()
        )
        items = list(
            (
                await self.session.execute(
                    base.order_by(StockMovement.id.desc()).limit(limit).offset(offset)
                )
            )
            .scalars()
            .all()
        )
        return items, total
