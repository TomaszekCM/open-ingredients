from datetime import timedelta

from app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_and_verify_success() -> None:
    password = "my-strong-password"

    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash)


def test_verify_password_fails_for_wrong_password() -> None:
    password_hash = hash_password("correct-password")

    assert not verify_password("wrong-password", password_hash)


def test_create_access_token_contains_subject() -> None:
    token = create_access_token("user@example.com", expires_delta=timedelta(minutes=5))

    payload = decode_access_token(token)

    assert payload["sub"] == "user@example.com"
    assert "exp" in payload
