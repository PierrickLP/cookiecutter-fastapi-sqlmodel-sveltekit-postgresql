from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app import crud, models
from app.api import deps
from app.core import security
from app.core.config import settings
from app.utils import (
    generate_password_reset_token,
    send_reset_password_email,
    verify_password_reset_token,
)

router = APIRouter()


@router.post("/login/access-token", response_model=models.Token)
async def login_access_token(
    db: deps.AsyncGetDbDep,
    *,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/login/test-token", response_model=models.UserReadWithItems)
def test_token(*, current_user: deps.CurrentUserDep) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}", response_model=models.Msg)
async def recover_password(db: deps.AsyncGetDbDep, *, email: str) -> Any:
    """
    Password Recovery
    """
    user = await crud.user.get_by_email(db, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    send_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    return {"msg": "Password recovery email sent"}


@router.post("/reset-password/", response_model=models.Msg)
async def reset_password(
    db: deps.AsyncGetDbDep,
    *,
    token: str = Body(...),
    new_password: str = Body(...),
) -> Any:
    """
    Reset password
    """
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = await crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    await crud.user.update(db, db_obj=user, obj_in={"password": new_password})
    return {"msg": "Password updated successfully"}
