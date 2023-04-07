from typing import Annotated, AsyncGenerator, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError
from pydantic import ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession

from app import crud, models
from app.core import security
from app.core.config import settings
from app.db.session import AsyncSession, Session

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator:
    with Session() as session:
        yield session


async def async_get_db() -> AsyncGenerator:
    async with AsyncSession() as session:
        yield session


AsyncGetDbDep = Annotated[SQLModelAsyncSession, Depends(async_get_db)]


async def get_current_user(
    db: AsyncGetDbDep,
    token: Annotated[str, Depends(reusable_oauth2)],
) -> models.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = models.TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


CurrentUserDep = Annotated[models.User, Depends(get_current_user)]


def get_current_active_user(
    current_user: CurrentUserDep,
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


CurrentActiveUserDep = Annotated[models.User, Depends(get_current_active_user)]


def get_current_active_superuser(
    current_user: CurrentActiveUserDep,
) -> models.User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


CurrentActiveSuperuserDep = Annotated[
    models.User, Depends(get_current_active_superuser)
]
