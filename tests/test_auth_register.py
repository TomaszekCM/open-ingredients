from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.models import User, UserRole


def _build_test_db_session() -> tuple[sessionmaker, object]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False), engine


def test_register_creates_user_and_returns_token() -> None:
    TestingSessionLocal, _engine = _build_test_db_session()

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.post(
        "/auth/register",
        json={
            "email": "new-user@example.com",
            "password": "very-strong-password",
            "confirm_password": "very-strong-password",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"

    with TestingSessionLocal() as db:
        user = db.scalar(select(User).where(User.email == "new-user@example.com"))
        assert user is not None
        assert user.role == UserRole.USER
        assert user.tenant_id is None
        assert user.password_hash is not None
        assert user.password_hash != "very-strong-password"

    app.dependency_overrides.clear()


def test_register_rejects_duplicate_email() -> None:
    TestingSessionLocal, _engine = _build_test_db_session()

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    payload = {
        "email": "dup@example.com",
        "password": "very-strong-password",
        "confirm_password": "very-strong-password",
    }
    first = client.post("/auth/register", json=payload)
    second = client.post("/auth/register", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["detail"] == "Email already registered"

    app.dependency_overrides.clear()
