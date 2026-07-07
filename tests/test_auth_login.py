from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.models import User, UserRole
from app.security import hash_password


def _build_test_db_session() -> tuple[sessionmaker, object]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False), engine


def test_login_returns_token_for_valid_credentials() -> None:
    TestingSessionLocal, _engine = _build_test_db_session()

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    with TestingSessionLocal() as db:
        db.add(
            User(
                email="login-ok@example.com",
                password_hash=hash_password("very-strong-password"),
                role=UserRole.USER,
            )
        )
        db.commit()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.post(
        "/auth/login",
        json={"email": "login-ok@example.com", "password": "very-strong-password"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"

    app.dependency_overrides.clear()


def test_login_rejects_invalid_password() -> None:
    TestingSessionLocal, _engine = _build_test_db_session()

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    with TestingSessionLocal() as db:
        db.add(
            User(
                email="login-fail@example.com",
                password_hash=hash_password("correct-password"),
                role=UserRole.USER,
            )
        )
        db.commit()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.post(
        "/auth/login",
        json={"email": "login-fail@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

    app.dependency_overrides.clear()


def test_login_rejects_unknown_email() -> None:
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
        "/auth/login",
        json={"email": "missing@example.com", "password": "some-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

    app.dependency_overrides.clear()


def test_login_rejects_user_without_password_hash() -> None:
    TestingSessionLocal, _engine = _build_test_db_session()

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    with TestingSessionLocal() as db:
        db.add(
            User(
                email="oauth-only@example.com",
                password_hash=None,
                role=UserRole.USER,
            )
        )
        db.commit()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.post(
        "/auth/login",
        json={"email": "oauth-only@example.com", "password": "any-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

    app.dependency_overrides.clear()
