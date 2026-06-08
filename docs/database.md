# Database Design

## Core Concepts

The platform is built around hierarchical ingredient compositions.

Each company (tenant) owns its own products and data.

Products are versioned. Editing a product creates a new product version.

Each product version has a dedicated QR code that resolves to that exact version.

A product consists of ingredients.

An ingredient may itself consist of other ingredients.

This allows complete ingredient traceability across multiple levels.

Example:

Bread
├── Flour
├── Water
└── Salt
	├── Sodium Chloride
	└── Anti-caking Agent E535

## Entities

### Tenant

Represents a company workspace and isolation boundary.

All business entities are linked to a tenant.

### User

Represents a system user.

Roles:

* Consumer
* Manufacturer
* Administrator

Authentication providers:

* Consumer: email/password
* Manufacturer: Google OAuth

### Company

Represents a food manufacturer.

A company can own multiple products.

### Product

Represents a logical product (for example "Dark Chocolate 70%").

Contains stable identity fields and belongs to one tenant.

### ProductVersion

Represents one immutable snapshot of a product.

Examples:

* Product X v1
* Product X v2

Contains:

* version number
* label fields shown to users
* publication status
* created at / published at

Ingredient composition is attached to ProductVersion, not Product.

Examples:

* Bread
* Yogurt
* Chocolate

### Ingredient

Represents a reusable ingredient definition.

Examples:

* Salt
* Sugar
* Flour
* E500ii

Ingredients may be shared between products.

### ProductVersionIngredient

Many-to-many relation between ProductVersion and Ingredient.

Stores:

* quantity
* percentage
* ordering

### IngredientComposition

Self-referencing relation.

Allows ingredients to contain sub-ingredients.

Example:

Salt
-> E535
-> E536

Chocolate Filling
-> Sugar
-> Cocoa
-> Emulsifier

Rules:

* No cycles allowed
* Parent and child ingredients must belong to the same tenant
* Max depth limit enforced at API layer

Depth handling strategy (recommended):

* Default tree response is limited to a configured depth (for example depth 4)
* If a branch exceeds the limit, API returns a truncated node marked as expandable
* UI shows "show sub-composition" action for truncated semi-products
* Clicking expandable node triggers a dedicated endpoint for that semi-product subtree
* Deeper semi-products can be managed as reusable ingredients and linked across products

Why this pattern:

* Protects recursive queries from excessive depth and unstable latency
* Keeps first product page load fast
* Preserves full transparency through progressive expansion

### ProductView

Stores product access statistics.

Attributes:

* product
* product version
* timestamp
* country
* user

History is stored only when user is authenticated.

### QRCode

Represents generated QR codes associated with product versions.

Rules:

* One active QRCode per ProductVersion
* QR destination is immutable
* New ProductVersion requires a new QRCode

## Planned Relationships

Tenant
|
+-- Company
|
+-- User
|
+-- Product
	|
	+-- ProductVersion
		|
		+-- ProductVersionIngredient
			|
			+-- Ingredient
				|
				+-- IngredientComposition
|
+-- QRCode (points to ProductVersion)
|
+-- ProductView (optional user reference)

## Multi-Tenant Rules

* Every domain table contains tenant_id
* Unique constraints include tenant_id where needed
* Cross-tenant references are forbidden
* Authorization must always filter by tenant_id

### External Branded Semi-Products

Scenario:
Tenant X uses a branded semi-product produced by Tenant Y (for example cookies used in ice cream).

Policy:

* Tenant X cannot create direct foreign keys to private ingredient records owned by Tenant Y
* Tenant X creates its own tenant-scoped ingredient entry for the branded semi-product
* Source metadata is stored on Tenant X side (brand name, supplier, declared source, batch/reference)
* ProductVersion stores a composition snapshot so history stays immutable for QR-linked versions
* Optional public reference can be stored as a non-FK external identifier when available

Rationale:

* Preserves tenant isolation and prevents cross-tenant data leakage
* Keeps version history legally and operationally auditable
* Allows using external products without coupling tenant data models

## Future Extensions

* Product categories and tags
* Product change history
* Row-level security policies
