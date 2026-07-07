import pytest
from pydantic import ValidationError

from app.schemas.auth import LoginRequest, RegisterRequest


def test_register_request_rejects_short_password() -> None:
    with pytest.raises(ValidationError):
        RegisterRequest(
            email="user@example.com",
            password="short",
            confirm_password="short",
        )


def test_register_request_rejects_mismatched_passwords() -> None:
    with pytest.raises(ValidationError):
        RegisterRequest(
            email="user@example.com",
            password="long-enough",
            confirm_password="different-pass",
        )


def test_login_request_accepts_valid_payload() -> None:
    payload = LoginRequest(email="user@example.com", password="long-enough")

    assert payload.email == "user@example.com"
    assert payload.password == "long-enough"
