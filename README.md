# OpenIngredients

OpenIngredients is a platform designed to improve food ingredient transparency.

The project allows manufacturers to publish complete product compositions, including ingredients of intermediate products and additives that are often omitted from traditional packaging labels.

Each product receives a QR code that can be scanned by consumers to access detailed ingredient information online.

## Product Principles

* Multi-tenant from day one (many companies in one platform)
* Product editing creates a new immutable product version (v1, v2, ...)
* Every product version gets its own QR code
* QR code always resolves to one specific product version
* Public product browsing is available without login
* View history is stored only for authenticated consumer accounts

## Goals

* Full ingredient traceability
* QR-code based product identification
* Public product search
* Manufacturer self-service portal
* Mobile application for consumers
* Scalable cloud-native architecture

## Planned Features

### Consumer Features

* Product search
* Category filtering
* Product details page
* QR code scanning
* Ingredient composition tree
* Version timeline (current and previous product versions)
* Viewing history for logged-in consumers only

### Manufacturer Features

* Google OAuth login
* Product management
* Product version management
* Ingredient management
* QR code generation
* Analytics dashboard

### Administration

* Manufacturer verification
* Product moderation
* Tenant management
* Reporting

### Administration Approach (Practical UX)

* Start with a lightweight backoffice, not a full enterprise admin suite
* Moderate product versions (v1, v2, ...), not whole products
* Keep a review queue as the main admin screen (reports, risky changes, verification tasks)
* Require audit log entries for every critical admin action (who, what, when, why)
* Use role-based admin access (support, compliance, super admin)

MVP administration scope:

* Manufacturer verification workflow (pending, verified, suspended)
* Product version moderation actions (approve, hide, request fixes)
* Reports queue with status tracking (new, in progress, resolved, dismissed)
* Tenant-level operational controls and visibility

## Technology Stack

### Backend

* FastAPI
* SQLAlchemy
* PostgreSQL
* Redis (phase-in after MVP)
* RabbitMQ (phase-in after MVP)
* Celery (phase-in after MVP)

### Frontend

* React
* TypeScript
* TanStack Query

### Infrastructure

* Docker
* AWS S3
* Prometheus
* Grafana

## Project Status

Early development.

See `/docs` for architecture, database design and roadmap.

Key planning docs:

* `/docs/adr.md` - architecture decisions
* `/docs/commit-checklist.md` - starter small-commit implementation plan

## Local JWT Secret

Authentication uses JWT signed with `JWT_SECRET_KEY` from environment variables.

For local development:

* copy values from `.env.example`
* set `JWT_SECRET_KEY` to a long random string

Example secret generation:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```
