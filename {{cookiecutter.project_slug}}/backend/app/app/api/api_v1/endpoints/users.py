from typing import Any

from fastapi import APIRouter, Body, HTTPException
from pydantic.networks import EmailStr

from app import crud, models
from app.api import deps
from app.core.config import settings
from app.utils import send_new_account_email

router = APIRouter()


@router.get("/", response_model=list[models.UserReadWithItems])
async def read_users(
    db: deps.AsyncGetDbDep,
    *,
    current_user: deps.CurrentActiveSuperuserDep,
    offset: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve users.
    """
    users = await crud.user.get_multi(db, offset=offset, limit=limit)
    return users


@router.post("/", response_model=models.UserReadWithItems)
async def create_user(
    db: deps.AsyncGetDbDep,
    *,
    user_in: models.UserCreate,
    current_user: deps.CurrentActiveSuperuserDep,
) -> Any:
    """
    Create new user.
    """
    user = await crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = await crud.user.create(db, obj_in=user_in)
    if settings.EMAILS_ENABLED:
        send_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
    return user


@router.patch("/me", response_model=models.UserReadWithItems)
async def update_user_me(
    db: deps.AsyncGetDbDep,
    *,
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: deps.CurrentActiveUserDep,
) -> Any:
    """
    Update own user.
    """
    user_in = models.UserUpdate()
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = await crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me", response_model=models.UserReadWithItems)
async def read_user_me(
    current_user: deps.CurrentActiveUserDep,
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.post("/open", response_model=models.UserReadWithItems)
async def create_user_open(
    db: deps.AsyncGetDbDep,
    *,
    password: str = Body(...),
    email: EmailStr = Body(...),
    full_name: str = Body(None),
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )
    user = await crud.user.get_by_email(db, email=email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user_in = models.UserCreate(password=password, email=email, full_name=full_name)
    user = await crud.user.create(db, obj_in=user_in)
    return user


@router.get("/{user_id}", response_model=models.UserReadWithItems)
async def read_user_by_id(
    db: deps.AsyncGetDbDep,
    *,
    user_id: int,
    current_user: deps.CurrentActiveUserDep,
) -> Any:
    """
    Get a specific user by id.
    """
    user = await crud.user.get(db, id=user_id)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    return user


@router.patch("/{user_id}", response_model=models.UserReadWithItems)
async def update_user(
    db: deps.AsyncGetDbDep,
    *,
    user_id: int,
    user_in: models.UserUpdate,
    current_user: deps.CurrentActiveSuperuserDep,
) -> Any:
    """
    Update a user.
    """
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = await crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}", response_model=models.UserReadWithItems)
async def delete_user(
    db: deps.AsyncGetDbDep,
    *,
    user_id: int,
    current_user: deps.CurrentActiveSuperuserDep,
) -> Any:
    """
    Delete a user.
    """
    user = await read_user_by_id(db, user_id=user_id, current_user=current_user)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = await crud.user.remove(db, db_obj=user)
    return user
