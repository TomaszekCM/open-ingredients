from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.models import User, UserRole
from app.security import create_access_token, hash_password


def _build_test_db_session() -> tuple[sessionmaker, object]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False), engine


def test_me_returns_current_user_for_valid_token() -> None:
    TestingSessionLocal, _engine = _build_test_db_session()

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    with TestingSessionLocal() as db:
        user = User(
            email="me-ok@example.com",
            password_hash=hash_password("very-strong-password"),
            role=UserRole.USER,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        access_token = create_access_token(subject=str(user.id))

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "me-ok@example.com"
    assert body["role"] == "user"
    assert body["tenant_id"] is None

    app.dependency_overrides.clear()


def test_me_requires_authorization_header() -> None:
    TestingSessionLocal, _engine = _build_test_db_session()

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

    app.dependency_overrides.clear()


def test_me_rejects_invalid_token() -> None:
    TestingSessionLocal, _engine = _build_test_db_session()

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer not-a-real-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

    app.dependency_overrides.clear()
