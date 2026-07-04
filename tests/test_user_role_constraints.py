import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models import Tenant, User, UserRole


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        yield session


def test_manufacturer_requires_tenant(db_session) -> None:
    user = User(email="manufacturer-no-tenant@example.com", role=UserRole.MANUFACTURER)
    db_session.add(user)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_admin_must_not_have_tenant(db_session) -> None:
    tenant = Tenant(name="Acme")
    db_session.add(tenant)
    db_session.commit()

    admin = User(email="admin-with-tenant@example.com", role=UserRole.ADMIN, tenant_id=tenant.id)
    db_session.add(admin)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_user_email_is_globally_unique(db_session) -> None:
    tenant = Tenant(name="Globex")
    db_session.add(tenant)
    db_session.commit()

    first = User(email="same@example.com", role=UserRole.USER)
    second = User(
        email="same@example.com",
        role=UserRole.MANUFACTURER,
        tenant_id=tenant.id,
    )

    db_session.add(first)
    db_session.commit()
    db_session.add(second)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_admin_without_tenant_is_allowed(db_session) -> None:
    admin = User(email="global-admin@example.com", role=UserRole.ADMIN)
    db_session.add(admin)
    db_session.commit()

    stored = db_session.query(User).filter_by(email="global-admin@example.com").one()
    assert stored.tenant_id is None
