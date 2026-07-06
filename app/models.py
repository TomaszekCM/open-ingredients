import enum

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class UserRole(str, enum.Enum):
    # USER: regular account, may exist without tenant/company binding.
    USER = "user"
    # MANUFACTURER: tenant-scoped business account.
    MANUFACTURER = "manufacturer"
    # ADMIN: system-wide administrative account, not company-bound.
    ADMIN = "admin"


class Tenant(Base):
    __tablename__ = "tenants"

    # Tenant is the top-level isolation boundary for all business data.
    # In practice, one producer organization maps to one tenant.

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    users: Mapped[list["User"]] = relationship(back_populates="tenant")
    companies: Mapped[list["Company"]] = relationship(back_populates="tenant")
    company_memberships: Mapped[list["CompanyMembership"]] = relationship(
        back_populates="tenant",
        overlaps="company_memberships,user_memberships,user,company",
    )


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_users_tenant_id_id"),
        UniqueConstraint("email", name="uq_users_email"),
        CheckConstraint(
            "(role != 'MANUFACTURER') OR (tenant_id IS NOT NULL)",
            name="ck_users_manufacturer_requires_tenant",
        ),
        CheckConstraint(
            "(role != 'ADMIN') OR (tenant_id IS NULL)",
            name="ck_users_admin_without_tenant",
        ),
    )

    # Public browsing does not depend on this role; it is available to everyone.
    # In this demo, regular USER accounts may exist without tenant assignment.
    # MANUFACTURER accounts are tenant-scoped.
    # ADMIN accounts are global and must not be tenant/company bound.
    # password_hash is populated for email/password accounts.

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int | None] = mapped_column(
        ForeignKey("tenants.id"), nullable=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), nullable=False
    )

    tenant: Mapped[Tenant | None] = relationship(back_populates="users")
    company_memberships: Mapped[list["CompanyMembership"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        overlaps="company_memberships,user_memberships,tenant,company",
    )
    companies: Mapped[list["Company"]] = relationship(
        secondary="company_memberships", back_populates="users", viewonly=True
    )


class Company(Base):
    __tablename__ = "companies"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_companies_tenant_name"),
        UniqueConstraint("tenant_id", "id", name="uq_companies_tenant_id_id"),
    )

    # Company is the business entity represented inside a tenant.
    # A tenant may stay close to one company in this demo app, but the model leaves
    # room for one tenant to hold multiple companies if needed later.

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    tenant: Mapped[Tenant] = relationship(back_populates="companies")
    user_memberships: Mapped[list["CompanyMembership"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
        overlaps="company_memberships,tenant,user",
    )
    users: Mapped[list[User]] = relationship(
        secondary="company_memberships", back_populates="companies", viewonly=True
    )


class CompanyMembership(Base):
    __tablename__ = "company_memberships"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "user_id",
            "company_id",
            name="uq_company_memberships_tenant_user_company",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "user_id"],
            ["users.tenant_id", "users.id"],
            name="fk_company_memberships_user",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "company_id"],
            ["companies.tenant_id", "companies.id"],
            name="fk_company_memberships_company",
        ),
    )

    # Simple many-to-many membership table.
    # It allows one user to belong to many companies without introducing
    # per-company roles or extra permission complexity at this stage.

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(nullable=False)
    company_id: Mapped[int] = mapped_column(nullable=False)

    tenant: Mapped[Tenant] = relationship(
        back_populates="company_memberships",
        overlaps="company_memberships,user_memberships,user,company",
    )
    user: Mapped[User] = relationship(
        back_populates="company_memberships",
        overlaps="company_memberships,tenant,user_memberships,company",
    )
    company: Mapped[Company] = relationship(
        back_populates="user_memberships",
        overlaps="company_memberships,tenant,user_memberships,user",
    )
