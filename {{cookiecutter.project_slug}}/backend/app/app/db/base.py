# Import all the models, so that Base has them before being
# imported by Alembic
from sqlmodel import SQLModel  # noqa: F401

from app.models.item import Item  # noqa: F401
from app.models.user import User  # noqa: F401
