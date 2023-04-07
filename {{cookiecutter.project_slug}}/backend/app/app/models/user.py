from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .item import Item, ItemRead


# Shared properties
class UserBase(SQLModel):
    full_name: str | None = Field(default=None, index=True)
    email: EmailStr = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False


# Additional properties stored in DB
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    hashed_password: str

    items: list["Item"] = Relationship(
        back_populates="owner", sa_relationship_kwargs={"lazy": "selectin"}
    )  # XXX: check lazy selectin


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str


# Properties to return via API
class UserRead(UserBase):
    id: int


class UserReadWithItems(UserRead):
    items: list["ItemRead"] = []


# Properties to receive via API on update
class UserUpdate(SQLModel):
    full_name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
