import typing
from typing import Any, Generic, Type, TypeVar

from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLModel table class
        """
        self.model = model

    # https://github.com/tiangolo/sqlmodel/issues/54#issuecomment-907935531
    @typing.no_type_check
    async def get(self, db: AsyncSession, id: int) -> ModelType | None:
        result = await db.exec(select(self.model).where(self.model.id == id))
        return result.first()

    # https://github.com/tiangolo/sqlmodel/issues/54#issuecomment-907935531
    @typing.no_type_check
    async def get_multi(
        self, db: AsyncSession, *, offset: int = 0, limit: int = 100
    ) -> list[ModelType]:
        result = await db.exec(select(self.model).offset(offset).limit(limit))
        return result.all()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model.from_orm(obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, db_obj: ModelType) -> ModelType:
        await db.delete(db_obj)
        await db.commit()
        return db_obj
