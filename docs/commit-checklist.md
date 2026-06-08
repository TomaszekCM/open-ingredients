# Initial Implementation Commit Checklist

This checklist defines small, reversible starter commits for the first implementation cycle.

Rules:
* One commit = one clear responsibility.
* Keep schema, API, and UI changes separated where possible.
* Add tests in the same commit as behavior changes.

---

## 1. chore(repo): bootstrap backend skeleton

Scope:
* Create FastAPI app entrypoint and package structure.
* Add basic health endpoint.
* Add pyproject and dependency lock strategy.

Done when:
* App starts locally.
* /health returns 200.

---

## 2. chore(dev): docker-compose for local services

Scope:
* Add PostgreSQL service.
* Add app service for local development.
* Add environment template.

Done when:
* Local stack boots with one command.
* App can connect to local PostgreSQL.

---

## 3. chore(db): initialize SQLAlchemy and Alembic

Scope:
* Add DB engine/session config.
* Initialize Alembic.
* Add first empty migration.

Done when:
* alembic upgrade head works on clean DB.

---

## 4. chore(ci): bootstrap minimal CI workflow

Scope:
* Add a basic CI workflow file.
* Run on push and pull request.
* Verify the workflow executes at least one simple check.

Done when:
* CI workflow is visible in the repository.
* A push to the main development branch shows at least one green check.

Note:
* PRs are optional for solo development and can be used later for self-review if desired.

---

## 5. feat(db): add tenant and user-role schema

Scope:
* Add Tenant, User, Company tables.
* Add role enum and key constraints.
* Include tenant_id where required.

Done when:
* Migration applies cleanly.
* Basic tenant isolation constraints exist.

---

## 6. feat(auth): consumer email/password auth

Scope:
* Register/login endpoints for consumers.
* JWT issue/refresh flow.
* Password hashing and validation.

Done when:
* Consumer can register and call protected endpoint.
* Auth tests pass.

---

## 7. feat(auth): Google OAuth for manufacturers

Scope:
* Google OAuth login callback flow.
* Manufacturer role assignment.
* Company/tenant binding on onboarding.

Done when:
* Manufacturer can sign in with Google in dev setup.
* Tenant binding is persisted.

---

## 8. feat(db): product and immutable product_version model

Scope:
* Add Product and ProductVersion tables.
* Add version number and publication status.
* Prevent in-place mutation of published version data.

Done when:
* New version creation path works.
* Tests verify immutability rules.

---

## 9. feat(db): ingredient and composition schema

Scope:
* Add Ingredient, ProductVersionIngredient, IngredientComposition.
* Enforce same-tenant parent/child links.
* Add cycle-prevention validation layer.

Done when:
* Composition graph can be saved and read.
* Cycle attempts are rejected.

---

## 10. feat(api): recursive composition endpoints with depth limit

Scope:
* Add product version composition endpoint.
* Add configurable max_depth parameter (bounded by server max).
* Return expandable markers for truncated nodes.

Done when:
* Deep trees return stable response times.
* Tests cover truncation and expandability markers.

---

## 11. feat(qr): QR bound to product version

Scope:
* Add QRCode table and generation service.
* Map QR to immutable product version identifier.
* Add QR lookup endpoint.

Done when:
* Scanning QR resolves exact product version.
* New product version produces new QR.

---

## 12. feat(api): public read endpoints and authenticated history

Scope:
* Public search by name/category.
* Public product version details endpoint.
* ProductView write only when user is authenticated.

Done when:
* Anonymous read works without login.
* Personal history stores only logged-in views.

---

## 13. test(ci): quality gates and tenant isolation checks

Scope:
* Add CI workflow for lint, tests, migrations.
* Add integration tests for cross-tenant access denial.
* Add regression tests for version and QR immutability.

Done when:
* CI green on clean clone.
* Security-critical tests are mandatory in pipeline.

---

## Suggested tags for grouping commits

* Foundation: 1-4
* Identity and tenancy: 5-7
* Product core: 8-11
* Public experience and hardening: 12-13
