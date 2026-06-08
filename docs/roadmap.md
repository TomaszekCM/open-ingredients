# Roadmap

## Vision

OpenIngredients aims to provide complete food ingredient transparency through publicly accessible product composition data.

Consumers should be able to scan a QR code and inspect the full composition of a product, including nested ingredients and additives.

The project also serves as a learning platform for modern backend, frontend and cloud-native technologies.

## Delivery Strategy

* Build for multi-tenant support from day one
* Treat product versions as immutable snapshots
* Generate a new QR for every new product version
* Keep commits small and reversible
* Add infrastructure complexity only when justified by measured load

## Deployment Strategy

* Start in budget mode with a single AWS account
* Prefer the simplest viable cloud setup over enterprise-grade multi-account governance
* Keep dev/staging/prod separation logical at first, not necessarily as separate AWS accounts
* Introduce AWS Organizations, SCP, and multi-account setups only when the project and budget justify it
* Optimize for learning, delivery, and low operational cost before cloud sophistication

---

# Phase 1 — Project Foundation

Status: Planned

Goals:

* Create FastAPI application
* Configure PostgreSQL for local development
* Configure SQLAlchemy
* Configure Alembic migrations
* Dockerize development environment
* Add CI checks (lint, tests, formatting)
* Enforce day-0 secret hygiene (no secrets in repository)

Deliverables:

* Running API
* Running PostgreSQL service (local)
* Database migrations
* Swagger documentation
* Docker Compose setup
* Basic CI pipeline
* Secret-safe repository baseline (`.env.example`, `.gitignore`, no hardcoded secrets)

Basic CI pipeline includes:

* Trigger on push and pull request
* Dependency installation and project setup
* Lint and formatting checks
* Automated test run
* Migration check (`alembic upgrade head` on clean database)
* Optional API smoke test (`/health`)
* Required green status checks before merge
* Basic secret scan check

---

# Phase 2 — Identity, Roles and Tenants

Status: Planned

Goals:

* Implement tenant model
* Implement user model with roles (consumer, manufacturer, admin)
* Add consumer email/password auth
* Add manufacturer Google OAuth
* Add tenant-aware authorization rules

Deliverables:

* Auth API
* Role and tenant guardrails
* Integration tests for tenant isolation

---

# Phase 3 — Product and Version Model

Status: Planned

Goals:

* Implement Product and immutable ProductVersion
* Define publication states (draft, published, archived)
* Add version timeline endpoint
* Enforce "edit product = create new version"

Deliverables:

* Product and version API
* Versioning rules with tests

---

# Phase 4 — Ingredients and Recursive Composition

Status: Planned

Goals:

* Implement Ingredient and IngredientComposition
* Attach composition to ProductVersion
* Enforce acyclic composition graph
* Add recursive composition read API

Deliverables:

* Ingredient management API
* Recursive composition endpoint
* Validation for cycles and depth limit

---

# Phase 5 — Public Read Experience

Status: Planned

Goals:

* Public product search by name and category
* Public product version page
* Public composition tree visualization
* No login required for read path

Deliverables:

* Public search endpoint and UI-ready response
* Public product version endpoint

---

# Phase 6 — QR Code Workflow

Status: Planned

Goals:

* Generate QR for each published ProductVersion
* Ensure QR points to exact immutable version page
* Regenerate QR only when a new version is created

Deliverables:

* QR generation endpoint/job
* QR lookup endpoint
* Tests for QR/version immutability

---

# Phase 7 — React Web Frontend

Status: Planned

Goals:

* React application setup
* TypeScript integration
* Public product search and details
* Login screens for consumer and manufacturer
* Manufacturer dashboard
* Product version timeline UI

Deliverables:

* Fully functional web UI

---

# Phase 8 — Consumer History and Accounts

Status: Planned

Goals:

* Store view history only for authenticated consumers
* Add "my viewed products" endpoint
* Exclude anonymous traffic from personal history

Deliverables:

* Consumer history API
* History screens in frontend

---

# Phase 9 — Caching and Rate Limiting

Status: Planned

Goals:

* Redis integration
* Product and search caching
* Rate limiting for public endpoints

Deliverables:

* Reduced database load
* Better p95 latency on public read endpoints

---

# Phase 10 — Background Jobs

Status: Planned

Goals:

* Celery integration
* Move QR generation to async tasks
* Add image processing jobs
* Add periodic aggregation jobs

Deliverables:

* Worker infrastructure
* Async task execution

---

# Phase 11 — Event-Driven Extensions

Status: Planned

Goals:

* RabbitMQ integration
* Publish key domain events
* Add event consumers for analytics/integrations

Deliverables:

* Message broker
* Event publishing and consuming

---

# Phase 12 — Analytics

Status: Planned

Goals:

* Product view tracking
* Manufacturer analytics dashboard
* Tenant-level usage analytics
* Real-time dashboard updates for manufacturers (WebSocket or SSE)

Deliverables:

* Analytics API
* Dashboard endpoints
* Real-time events endpoint and live dashboard integration
* Polling fallback strategy for non-real-time clients

---

# Phase 13 — Cloud Infrastructure and Observability

Status: Planned

Goals:

* AWS deployment in budget mode
* AWS governance baseline (IAM least privilege, account boundaries)
* SCP policies via AWS Organizations (when multi-account setup is introduced)
* S3 integration for media/assets
* Prometheus metrics
* Grafana dashboards
* Structured logging and tracing

Deliverables:

* Production deployment
* Single-account cloud setup for initial deployment
* Cloud governance baseline (including SCP where applicable)
* Monitoring stack

---

# Phase 14 — Performance and Scale Validation

Status: Planned

Goals:

* Load testing
* Stress testing
* Benchmarking and bottleneck analysis

Deliverables:

* Performance reports
* Optimization plan

---

# Phase 15 — Kubernetes (Optional)

Status: Future

Goals:

* Kubernetes deployment
* Horizontal scaling
* Autoscaling

Deliverables:

* Production-grade orchestration


