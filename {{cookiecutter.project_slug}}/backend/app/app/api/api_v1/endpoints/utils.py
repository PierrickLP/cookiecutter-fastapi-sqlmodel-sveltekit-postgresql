from typing import Any

from fastapi import APIRouter
from pydantic.networks import EmailStr

from app import models
from app.api import deps
from app.utils import send_test_email

router = APIRouter()


@router.get("/ping/", response_model=str, status_code=200)
def ping() -> Any:
    """
    Ping.
    """
    return "OK"


@router.post("/test-email/", response_model=models.Msg, status_code=201)
def test_email(
    email_to: EmailStr,
    current_user: deps.CurrentActiveSuperuserDep,
) -> Any:
    """
    Test emails.
    """
    send_test_email(email_to=email_to)
    return {"msg": "Test email sent"}
