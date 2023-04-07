from typing import Any

from sqlmodel import SQLModel

from .item import Item, ItemCreate, ItemRead, ItemReadWithOwner, ItemUpdate
from .msg import Msg
from .token import Token, TokenPayload
from .user import User, UserCreate, UserRead, UserReadWithItems, UserUpdate

# fix circular import :
# https://github.com/tiangolo/sqlmodel/issues/121#issuecomment-1432898978


def get_subclasses(cls: Any) -> Any:
    for subclass in cls.__subclasses__():
        yield from get_subclasses(subclass)
        yield subclass


models_dict = {cls.__name__: cls for cls in get_subclasses(SQLModel)}

for cls in models_dict.values():
    cls.update_forward_refs(**models_dict)
