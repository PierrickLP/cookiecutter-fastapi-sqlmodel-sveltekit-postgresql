from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User, UserRead


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(index=True)
    description: str | None = Field(default=None, index=True)
    owner_id: int = Field(foreign_key="user.id")


# Additional properties stored in DB
class Item(ItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    owner: "User" = Relationship(
        back_populates="items", sa_relationship_kwargs={"lazy": "selectin"}
    )


# Properties to receive via API on creation
class ItemCreate(ItemBase):
    title: str
    owner_id: int


# Properties to return via API
class ItemRead(ItemBase):
    id: int


class ItemReadWithOwner(ItemRead):
    owner: "UserRead"


# Properties to receive via API on update
class ItemUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    owner_id: int | None = None
