# Architecture

## Overview

OpenIngredients follows a modular architecture designed to support future horizontal scaling.

The core architectural decisions are:

* Multi-tenant domain model from day one
* Versioned products with immutable product versions
* One QR code per product version (immutable public link)
* Public read access for product pages and search
* Authenticated-only personal history for consumers

The system consists of:

* Web frontend
* Mobile frontend
* API backend
* PostgreSQL database
* Redis cache
* RabbitMQ message broker
* Celery workers
* Object storage for images

## High-Level Architecture

Consumer / Manufacturer
|
v
React App
|
v
FastAPI API
|
+-------------------+-------------------+-------------------+
|                   |                   |                   |
v                   v                   v                   v
PostgreSQL          Redis               AWS S3              RabbitMQ (optional post-MVP)
															|
															v
												   Celery Workers (async jobs)

## Responsibilities

### FastAPI

* Authentication (Google OAuth for manufacturers, email/password for consumers)
* Tenant-aware authorization and data access
* Product management
* Product versioning (v1, v2, ...)
* Search
* QR generation and QR lookup
* Public product version pages
* Consumer view history (authenticated users only)
* API gateway

### PostgreSQL

* Tenants and company isolation
* Users and roles
* Products
* Product versions
* Ingredients
* Ingredient hierarchy edges
* QR codes mapped to product versions
* Product view history
* Analytics

### Redis

* Product cache
* Search cache
* Rate limiting

### RabbitMQ

* Domain events
* Asynchronous communication

Used after MVP when event volume and integration needs justify broker complexity.

### Celery

* QR generation
* Email delivery
* Statistics aggregation
* Image processing

### AWS S3

* Product images
* Generated assets

## Future Improvements

* Kubernetes deployment
* CDN support
* Multi-region architecture
* Full-text search engine
* Read replicas for PostgreSQL
