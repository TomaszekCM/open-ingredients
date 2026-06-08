# Architecture Decision Records (ADR)

This file captures the core architecture decisions for OpenIngredients.

Status legend:
* Accepted
* Superseded
* Proposed

---

## ADR-001: Multi-tenant Model from Day One

Status: Accepted
Date: 2026-06-03

Context:
The platform is designed for multiple manufacturers (companies) in one shared system. Retrofitting tenant isolation later usually causes high migration and security costs.

Decision:
All core domain entities are tenant-scoped from the first implementation stage.

Implementation Notes:
* Add tenant_id to all core domain tables.
* Ensure unique constraints include tenant_id when appropriate.
* Reject cross-tenant references at validation and database levels.
* Enforce tenant filters in every authorized query path.

Consequences:
* Better isolation and security from the start.
* Slightly higher initial complexity in schema and authorization.
* Avoids expensive future refactors.

---

## ADR-002: Product Versions Are Immutable Snapshots

Status: Accepted
Date: 2026-06-03

Context:
Ingredient compositions can change between production batches. Users must see exactly what belongs to the scanned item.

Decision:
Product edits create a new ProductVersion (v1, v2, ...). Existing versions are immutable.

Implementation Notes:
* Product contains stable identity.
* ProductVersion contains composition and public label snapshot.
* Published version data cannot be edited in place.

Consequences:
* Full traceability and legal defensibility.
* Simpler audit and rollback model.
* Requires explicit version creation workflow in manufacturer UI.

---

## ADR-003: QR Code Is Bound to ProductVersion

Status: Accepted
Date: 2026-06-03

Context:
A QR printed on packaging must always resolve to the exact composition of that item.

Decision:
Each ProductVersion has its own QR code. QR destination is immutable.

Implementation Notes:
* QR maps directly to product_version_id (or equivalent immutable public token).
* New ProductVersion requires new QR generation.
* Historical versions remain accessible by direct QR and version timeline.

Consequences:
* Correct behavior for mixed stock on shelves.
* Clear user trust model.
* Additional operational need to manage version-to-QR generation lifecycle.

---

## ADR-004: Ingredient Graph Is Acyclic and Depth-Limited

Status: Accepted
Date: 2026-06-03

Context:
Ingredient compositions can be deeply nested. Unbounded recursion can degrade performance and reliability.

Decision:
Ingredient composition is modeled as a tenant-scoped acyclic graph with API depth limits.

Implementation Notes:
* Disallow cycles in composition graph.
* Parent/child ingredients must stay in the same tenant.
* Default API depth limit for initial tree load.
* Mark deeper nodes as expandable and fetch subtrees lazily.

Consequences:
* Stable and predictable API latency.
* Better UX for deep compositions.
* Requires dedicated subtree endpoint and client-side progressive expansion flow.

---

## ADR-005: Split Authentication by User Type

Status: Accepted
Date: 2026-06-03

Context:
Manufacturers need quick onboarding with existing business identities; consumers need simple account creation.

Decision:
Manufacturers authenticate with Google OAuth - used here as a public proxy for real-world government/regulatory business identity systems that are not accessible for this project. 
Consumers use email/password accounts.

Implementation Notes:
* Shared user model with role-based authorization.
* Manufacturer onboarding includes company/tenant binding.
* Consumer auth supports personal history features.

Consequences:
* Better fit for both user groups.
* More auth paths to test.
* Clear role boundaries required in API guards.

---

## ADR-006: Public Read Access, Authenticated Personal History

Status: Accepted
Date: 2026-06-03

Context:
Product transparency should be publicly accessible. Personal tracking should only be attached to explicit user identity.

Decision:
Search and product/version pages are public. View history is written only for authenticated consumers.

Implementation Notes:
* Public endpoints must not require login.
* History write path requires authenticated user context.
* Anonymous traffic is aggregated only in non-personal analytics.

Consequences:
* Low entry barrier for consumers.
* Privacy-friendly personal history behavior.
* Requires strict separation of personal vs aggregate analytics.

---

## ADR-007: Progressive Infrastructure Complexity

Status: Accepted
Date: 2026-06-03

Context:
The project should remain teachable and maintainable while being ready to scale.

Decision:
Start with FastAPI + PostgreSQL + Docker + CI. Introduce Redis/Celery/RabbitMQ only when measurable load justifies each addition.

Implementation Notes:
* Define baseline SLO and p95 latency measurements.
* Add caching first, then background jobs, then broker/eventing.
* Keep each infrastructure introduction behind isolated commits and feature toggles where possible.

Consequences:
* Faster MVP delivery and learning feedback loop.
* Lower operational overhead in early phases.
* Requires discipline to delay non-essential complexity.

---

## ADR-008: FastAPI as Primary Backend Framework

Status: Accepted
Date: 2026-06-05

Context:
The project is API-first, includes recursive read paths, and may require async I/O optimization over time.

Decision:
Use FastAPI as the primary backend framework.

Alternatives considered:
* Django: strong batteries-included framework, but heavier for API-only start and more opinionated around monolithic patterns.
* Flask: lightweight and flexible, but would require more manual assembly for typing, validation, and API docs parity.

Implementation Notes:
* Use Pydantic models for request/response validation.
* Keep API modules domain-oriented (auth, product, composition, qr, analytics).
* Use OpenAPI as a contract-first communication artifact.

Consequences:
* Faster API iteration with built-in docs and type-friendly patterns.
* Good async path when load grows.
* Team must stay disciplined about architecture because framework is intentionally flexible.

---

## ADR-009: React + TypeScript for Web Frontend

Status: Accepted
Date: 2026-06-05

Context:
The frontend includes public product browsing, manufacturer dashboards, and potentially real-time analytics views.

Decision:
Use React with TypeScript for the web application.

Alternatives considered:
* Vue: strong developer experience, but less aligned with current learning goals.
* Angular: robust enterprise structure, but higher initial complexity for MVP velocity.

Implementation Notes:
* Keep UI split by app areas (public, manufacturer, admin).
* Use strict TypeScript settings for API contract safety.
* Treat composition tree rendering as a dedicated reusable component.

Consequences:
* Large ecosystem and hiring/training familiarity.
* Better maintainability for growing UI complexity.
* Requires good component boundaries to avoid dashboard sprawl.

---

## ADR-010: PostgreSQL as Primary Relational Database

Status: Accepted
Date: 2026-06-05

Context:
The domain relies on relational integrity, version history, tenant isolation, and recursive composition queries.

Decision:
Use PostgreSQL as the primary database.

Alternatives considered:
* MySQL: capable relational option, but weaker fit for planned recursive/query ergonomics and JSON/advanced SQL flexibility.
* NoSQL-first approach: faster for some document use cases, but weaker for strict relational consistency and transactional history.

Implementation Notes:
* Use foreign keys and tenant-aware unique constraints.
* Use migrations for all schema evolution.
* Add indexing strategy for public read endpoints and tenant filters.

Consequences:
* Strong consistency and mature tooling.
* Good long-term fit for auditability and traceability.
* Requires careful query/index tuning for deep composition reads.

---

## ADR-011: Progressive Adoption of Redis, Celery, and RabbitMQ

Status: Accepted
Date: 2026-06-05

Context:
Early-stage systems often over-adopt infrastructure before demand appears, increasing operational burden.

Decision:
Introduce Redis, Celery, and RabbitMQ incrementally based on observed bottlenecks.

Alternatives considered:
* Add all infrastructure from day one: maximizes theoretical scalability but slows MVP and raises maintenance complexity.
* Avoid async/event stack entirely: simpler operations, but limits scaling and integration flexibility later.

Implementation Notes:
* Start with synchronous flow and measurement baselines.
* Add Redis first for read-path caching and rate limiting.
* Add Celery for long-running background tasks (QR generation, media processing).
* Add RabbitMQ when multi-consumer event workflows become a real requirement.

Consequences:
* Faster learning loop and delivery in early phases.
* Lower operational cost before product-market validation.
* Requires explicit readiness criteria for each technology introduction.
