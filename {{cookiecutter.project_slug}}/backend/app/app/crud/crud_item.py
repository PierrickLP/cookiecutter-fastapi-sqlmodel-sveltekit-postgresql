import typing

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import CRUDBase
from app.models.item import Item, ItemCreate, ItemUpdate


class CRUDItem(CRUDBase[Item, ItemCreate, ItemUpdate]):
    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: ItemCreate, owner_id: int
    ) -> Item:
        db_obj = Item.from_orm(obj_in, {"owner_id": owner_id})
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    # https://github.com/tiangolo/sqlmodel/issues/54#issuecomment-907935531
    @typing.no_type_check
    async def get_multi_by_owner(
        self, db: AsyncSession, *, owner_id: int, offset: int = 0, limit: int = 100
    ) -> list[Item]:
        result = await db.exec(
            select(Item).where(Item.owner_id == owner_id).offset(offset).limit(limit)
        )
        return result.all()


item = CRUDItem(Item)
