# Auto-Dealer-System-Backend

Project backend for an auto dealership system: user authentication, role-based access (customer/employee/admin), catalog management (cities/dealerships/models/vehicles), sales flows (orders and custom orders), customer activity (reviews, favorites, test drives), and an audit/logging subsystem.

## Contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Architecture and repository structure](#architecture-and-repository-structure)
- [Configuration](#configuration)
- [How to run](#how-to-run)
- [Database initialization](#database-initialization)
- [Deploying under your own brand](#deploying-under-your-own-brand)
- [API overview](#api-overview)
- [Authentication and sessions](#authentication-and-sessions)
- [Audit logging and reports (MongoDB)](#audit-logging-and-reports-mongodb)
- [Known limitations / important notes](#known-limitations--important-notes)
- [Troubleshooting](#troubleshooting)

## Features

- **Authentication**: signup, login, refresh, logout with JWT access/refresh tokens.
- **RBAC (roles)**: `customer`, `employee`, `admin` restrictions at endpoint level and in service logic.
- **Users and customers**: manage user accounts and customer profile records.
- **Reference data**: cities and dealerships.
- **Vehicle catalog**: models, features/options, and vehicles in stock.
- **Transactions**: orders (stock vehicles) and custom orders (factory-style).
- **Customer activity**: reviews, favorites, test drives.
- **Audit logs and reports**: store mutating actions and errors in MongoDB, query and export reports.
- **Caching / invalidation**: Redis cache + Redis Pub/Sub channel for cache invalidation on data changes.

## Tech stack

- **Python**: 3.12
- **Web framework**: FastAPI
- **SQL database**: PostgreSQL (async) via `asyncpg`
- **Cache / sessions / pubsub**: Redis (`redis.asyncio`)
- **Audit / analytics storage**: MongoDB (Motor)
- **Object storage**: S3-compatible (MinIO in Docker) via `aioboto3`
- **Dependency management**: Poetry (`pyproject.toml`)
- **Containerization**: Docker + Docker Compose (`Dockerfile`, `docker-compose.yaml`)

## Architecture and repository structure

The backend follows a layered structure:

- **API layer** (`src/api/`)\n
  - Versioned HTTP routes live in `src/api/v1/endpoints/`.\n
  - Routing aggregation: `src/api/v1/router.py`.\n
  - Security helpers: `src/api/security.py`.\n
  - RBAC decorator: `src/api/rbac.py`.\n
  - Dependencies (DI providers): `src/api/dependencies/`.\n
  - Middleware: `src/api/middlewares/` (audit logging).\n
  - Exception mapping: `src/api/exception_handlers.py`.\n
- **Application layer** (`src/application/`)\n
  - Services implement use cases (e.g. `src/application/services/auth_service.py`).\n
  - DTOs and mappers translate between API models and domain entities.\n
- **Domain layer** (`src/domain/`)\n
  - Entities, value objects, and abstractions/interfaces.\n
  - Domain exceptions (auth, tokens, business rules).\n
- **Infrastructure layer** (`src/infrastructure/`)\n
  - PostgreSQL connection/UoW/repositories.\n
  - Redis client/repositories/healthcheck.\n
  - MongoDB client + log repository.\n
  - S3 client implementation.\n
  - Startup helpers (e.g. employee seeding).\n

## Configuration

The application uses environment variables (Pydantic settings in `src/config.py`). A template is provided in `.env.example`.

### Required environment variables

Create a `.env` file at the repository root (next to `docker-compose.yaml`) with at least:

#### PostgreSQL

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_NAME`
- `POSTGRES_HOST` (when running locally without Docker, typically `localhost`)
- `POSTGRES_PORT` (typically `5432`)

#### Redis

- `REDIS_USER`
- `REDIS_PASSWORD` (Redis `requirepass`)\n
- `REDIS_USER_PASSWORD` (ACL user password)\n
- `REDIS_HOST` (typically `localhost`)\n
- `REDIS_PORT` (Docker compose maps to `6380` on host)

#### MongoDB (audit logs)

- `MONGO_HOST`
- `MONGO_PORT` (typically `27017`)
- `MONGO_USER`
- `MONGO_PASSWORD`
- `MONGO_DB` (default in compose: `audit_logs`)

#### JWT keys (RSA)

The backend expects an RSA key pair:

- `PRIVATE_KEY`: PEM string (PKCS8 recommended)
- `PUBLIC_KEY`: PEM string

Generate locally:

```bash
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out private_key.pem
openssl rsa -pubout -in private_key.pem -out public_key.pem
```

Then paste PEM contents into `.env` values (including the `-----BEGIN ...-----` / `-----END ...-----` lines).

#### S3 / MinIO (optional)

Media storage is **optional** in runtime: if `S3_ACCESS_KEY` / `S3_SECRET_ACCESS_KEY` are missing, the S3 client provider returns `None` (see `src/api/dependencies/s3.py`).

- `S3_ACCESS_KEY`
- `S3_SECRET_ACCESS_KEY`
- `S3_ENDPOINT_URL` (Docker: `http://minio:9000`, local host: typically `http://localhost:9000`)
- `S3_BUCKET_NAME` (default in compose: `auto-dealer-media`)
- `S3_REGION_NAME` (e.g. `us-east-1`)

### Docker-specific overrides

When running via Docker Compose, some connection settings are overridden for container-to-container networking in `docker-compose.yaml`:

- `POSTGRES_HOST=database`
- `REDIS_HOST=redis`
- `S3_ENDPOINT_URL=http://minio:9000`

## How to run

### Option A: Run with Docker Compose (recommended)

This brings up the backend and its dependencies (Postgres, Redis, MinIO, MongoDB). The compose file also contains a `frontend` service, but the backend can be used independently.

1) Create `.env` from `.env.example` and fill values.

2) Pull MinIO images **before** running compose.\n
`docker-compose.yaml` uses `pull_policy: never` for MinIO images, so you must have them locally:

```bash
docker pull minio/minio:latest
docker pull minio/mc:latest
```

3) Start services:

```bash
docker compose up --build
```

4) Backend is available at:

- API base: `http://localhost:8000/api/v1`
- OpenAPI docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Option B: Run locally (Poetry) + run dependencies separately

1) Install dependencies:

```bash
poetry install
```

2) Export env vars via `.env` (or your shell), ensure Postgres/Redis/Mongo are running locally.

3) Run FastAPI:

```bash
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## Database initialization

The schema is owned by versioned migrations; the app applies them on startup (`POSTGRES_MIGRATE_ON_START=true`).

| Path | Purpose |
|---|---|
| `db/migrations/NNNN_name.sql` | Forward-only migrations (DDL, triggers, functions/procedures). Applied in order, each in one transaction, checksum-verified |
| `brands/<pack>/catalog.yaml` | Catalog data of a brand pack (see [Deploying under your own brand](#deploying-under-your-own-brand)) |
| `db/queries/` | Reference SQL queries and reports (never executed automatically) |
| `db/dev/drop_all.sql` | Local helper that drops every object; never run it against shared environments |

Rules: never edit an applied migration (startup fails on checksum mismatch) - add a new `NNNN_*.sql` instead.
Databases created by the previous `initdb.d`/heuristic setup are adopted automatically as `0001_baseline`.

Load the catalog of the selected brand pack (`BRAND`, default `demo`); the importer applies pending migrations first:

```bash
docker compose --profile seed run --rm db-seed
```

### Vehicle and order integrity rules

Enforced by database triggers (`0003_vehicle_lifecycle_and_order_integrity.sql`), so they hold for every writer:

- `vehicles.status` (`in_stock`, `reserved`, `sold`, `service`, `unavailable`) replaces the old `is_active` flag.
- `reserved` and `sold` are driven only by orders: creating an order reserves the vehicle, completing it marks it sold,
  cancelling or deleting an active order releases it. Direct changes to these statuses are rejected.
- Only `in_stock` vehicles can be ordered or test-driven; the order dealership must match the vehicle's dealership.
- One non-cancelled order per vehicle (partial unique index); a cancelled vehicle can be ordered again.
- Order customer, vehicle and dealership are immutable; price changes only while `pending_payment`; status changes follow
  `pending_payment -> processing -> ready_for_pickup -> completed` (cancel allowed before completion); completed orders cannot be deleted.
- Vehicle price/status history and order/test-drive status history are written by triggers, including the initial row.
  The app passes the acting user and reason with `set_config('app.user_id' / 'app.change_reason', ..., true)`.
- Rule violations raise `P0001` errors that the API maps to HTTP 400 with the rule message.

### Models and trims

- A **model** is a body/line shared by every configuration (`A4 Sedan`: body type, production years, seats, dimensions).
- A **trim** is a sellable configuration of a model (`45 TFSI quattro`: engine, gearbox, drive type, speed, acceleration,
  tank, weights), unique by name within its model. Endpoints: `GET/POST /models/{id}/trims`, `GET/PATCH/DELETE /trims/{id}`.
- Vehicles and custom orders reference a **trim**; `model_id` is derived from it and a composite FK
  (`(trim_id, model_id) -> trims(id, model_id)`) makes it impossible to combine a trim with another model's id.
- A trim that is used by a vehicle or a custom order cannot be deleted. `GET /models?engine_id=` matches models having a trim with that engine.
- `0004_models_and_trims.sql` converts existing data: every old model becomes one model with one trim named after its engine;
  custom orders that asked for another engine/gearbox pair get an extra trim, so nothing is lost.

### Dealership pages

`0006_dealership_pages.sql` adds what a dealership page needs: `dealerships.description`, a photo gallery
(`dealership_media`, files in S3 under `dealerships/{id}/`), customer reviews (`dealership_reviews`, one per customer and
dealership) and a flat comment thread under each review (`dealership_review_comments`).

| Method | Path | Access | Purpose |
|---|---|---|---|
| GET | `/dealerships`, `/dealerships/{id}` | public | Also returns `description`, `rating_average`, `reviews_count`, `cover_url` |
| PATCH | `/dealerships/{id}` | dealership staff | Edit description, contacts, opening hours |
| GET | `/dealerships/managed` | employee/admin | Dealerships the user may manage |
| GET | `/dealerships/{id}/media`, `.../media/{media_id}/file` | public | Gallery and image files |
| POST, PATCH, DELETE | `/dealerships/{id}/media[/{media_id}]` | dealership staff | Upload (multipart), caption/order, delete |
| GET | `/dealerships/{id}/reviews?page&limit&include_hidden` | public | Reviews with comments and the rating summary; `include_hidden` is staff only |
| POST | `/dealerships/{id}/reviews` | customer | One review per dealership; the customer comes from the token |
| PATCH | `/dealerships/{id}/reviews/{review_id}` | review author | Edit rating, title, comment |
| DELETE | `/dealerships/{id}/reviews/{review_id}` | author or admin | Delete with its comments |
| PATCH | `/dealerships/{id}/reviews/{review_id}/visibility` | dealership staff | Hide or show (moderation) |
| POST | `/dealerships/{id}/reviews/{review_id}/comments` | author or dealership staff | Staff replies are marked `is_official` |
| DELETE | `/dealerships/{id}/reviews/{review_id}/comments/{comment_id}` | comment author or dealership staff | |

- **Dealership staff** means an admin, or an employee whose active `employee_profiles` row points to that dealership.
  Seeded employees get their profile from `dealership_id`/`position` in `employees.yaml` (created on startup once the
  dealership exists; an existing profile is never overwritten).
- Hidden reviews are excluded from the public list and from the rating, but their author still sees them.
- A review is marked `is_verified_customer` when its author has a non-cancelled order or a completed test drive in that
  dealership. The viewer's own review is returned first.

## Deploying under your own brand

The service is white-label: one backend image and one frontend image serve any make or dealer network.
A deployment is branded **only by configuration** - no code changes, no per-client image builds.
One deployment (stack + database) serves one brand; a multi-make dealer is one brand with a multi-make catalog.

### How it works

| Piece | Source of truth | Delivered via |
|---|---|---|
| Name, logo, colours, contacts, locale, currency, SEO, home texts/images, feature switches | `brand.yaml` (+ `BRAND__*` env overrides) | `GET /api/v1/brand` - the SPA fetches it at start and applies CSS variables, `<title>`, favicon, formatting |
| Brand assets (logo, favicon, images) | `<brand dir>/assets/` | `GET /api/v1/brand/assets/<file>` |
| Body types, engines, transmissions, fuel/transmission/drive codes | PostgreSQL | `GET /api/v1/lookups` |
| Models, trims, options, dealerships, vehicles | `catalog.yaml` of the brand pack | `python -m src.cli.import_catalog` |
| CORS origins, OpenAPI title | `server.*` in `brand.yaml` | backend only, never exposed |

### Brand packs

```
brands/<pack>/
  brand.yaml      # deploy-time brand config (validated at startup; the API refuses to start on errors)
  catalog.yaml    # catalog data (validated, idempotent import)
  assets/         # optional: logo.svg, favicon.svg, images referenced by file name
```

Shipped packs: `demo` (neutral fictional brand, default), `audi`, `toyota`.

### Steps

1. Copy `brands/demo` to `brands/<your-brand>` (or to any directory you mount into the container) and edit `brand.yaml`.
2. Point the backend to it:
   - Docker Compose in this repo: `BRAND=<your-brand> docker compose up -d app` (`./brands` is mounted read-only).
   - Any other runtime: mount the directory and set `BRAND_DIR=/path/in/container` (or `BRAND_CONFIG_FILE` for the YAML alone).
3. Load the catalog once (re-running is safe: existing rows are updated, values missing from the pack are kept):
   ```bash
   BRAND=<your-brand> docker compose --profile seed run --rm db-seed
   # or: docker compose run --rm app python -m src.cli.import_catalog /app/brands/<your-brand>/catalog.yaml
   # validate only: python -m src.cli.import_catalog --dry-run <file>
   ```
4. Serve the frontend image with `API_UPSTREAM=http://<backend>:8000`; nginx proxies `/api/` to it, so the same frontend image works for every brand.
5. Restart the backend after changing `brand.yaml`; browsers pick the new brand up on the next page load (`/brand` is revalidated via ETag on every load).

Local demo with a separate database per brand (the default database stays untouched):

```bash
docker exec database createdb -U <POSTGRES_USER> auto_dealer_toyota
BRAND=toyota BRAND_DB_NAME=auto_dealer_toyota docker compose --profile seed run --rm db-seed
BRAND=toyota BRAND_DB_NAME=auto_dealer_toyota docker compose up -d app
```

### Configuration reference

Every field is optional. Env overrides use `BRAND__` + the path with `__` as separator, e.g. `BRAND__THEME__ACCENT=#eb0a1e`,
`BRAND__FEATURES__CUSTOM_ORDERS=false`, `BRAND__SERVER__CORS_ORIGINS='["https://shop.example.com"]'` (lists/objects as JSON).
Precedence: env > `brand.yaml` > defaults.

Fields typed *text* accept either one string for every language or a per-language map,
e.g. `hero_title: { ru: "Ваш следующий Audi", en: "Your next Audi" }` (missing languages fall back to `ru`).
The UI is available in Russian and English: `locale.language` is the default, visitors can switch RU/EN in the header
(the choice is remembered in the browser).

| Field | Type | Default | Used in |
|---|---|---|---|
| `name` | string, 1-60 | `Auto Dealer` | header, footer, `<title>`, aria-labels, API title |
| `short_name` | string, 1-4 | initials of `name` | monogram logo and generated favicon |
| `tagline` | text \| null | null | under the name in the header |
| `legal_name` | string | = `name` | footer copyright |
| `logo_url` | asset file name or http(s) URL \| null | null (monogram) | header, footer |
| `favicon_url` | asset file name or http(s) URL \| null | null (monogram in accent colour) | browser tab |
| `locale.language` | `ru` \| `en` | `ru` | default UI language (visitors can switch), `<html lang>` |
| `locale.locale` | BCP 47 tag | `ru-RU` | number/date formatting and sorting in the default language (the other language uses `ru-RU` / `en-GB`) |
| `locale.currency` | ISO 4217 | `BYN` | prices (all prices of a deployment are in this currency) |
| `locale.country` | ISO 3166-1 alpha-2 | `BY` | reserved for region-specific behaviour |
| `locale.timezone` | IANA zone | `Europe/Minsk` | date/time formatting |
| `theme.accent` | `#rrggbb` | `#dc2626` | `--color-accent`: buttons, highlights |
| `theme.accent_strong` | `#rrggbb` | accent darkened 18% | `--color-accent-strong` (hover) |
| `theme.accent_subtle` | `#rrggbb` | accent lightened 93% | `--color-accent-subtle` |
| `theme.primary` | `#rrggbb` | `#1e293b` | `--color-primary`: header, dark sections, `theme-color` |
| `theme.primary_hover` | `#rrggbb` | primary lightened 12% | `--color-primary-hover` |
| `theme.focus` | `#rrggbb` | `#2563eb` | focus rings |
| `contacts.phone` | E.164 (`+375...`) \| null | null | header, footer, company page (`tel:`) |
| `contacts.phone_display` | string | = `phone` | how the phone is printed |
| `contacts.email` | email \| null | null | footer, company page |
| `contacts.address` | text \| null | null | footer, company page |
| `contacts.location_line` | text \| null | null | footer bottom line |
| `contacts.working_hours` | list of `{days, hours}` (both text) | `[]` | footer, company page |
| `contacts.service_hours_note` | text \| null | null | footer |
| `social` | list of `{type, url}`; type: website, instagram, facebook, telegram, vk, youtube, x, tiktok, whatsapp | `[]` | footer, company page |
| `seo.title` | text | `name` | `<title>` |
| `seo.description` | text | static text in `index.html` | meta description |
| `seo.og_image_url` | asset or URL \| null | null | `og:image` |
| `home.hero_kicker` / `hero_title` / `hero_subtitle` | text \| null | generic Russian copy | home page hero |
| `home.images.hero`, `.promo[0..2]`, `.tile_stock`, `.tile_test_drive`, `.tile_dealers`, `.service_maintenance`, `.service_booking`, `.service_parts` | asset or URL \| null | images bundled with the frontend | home page |
| `features.test_drives` | bool | true | menu, routes, home tiles; API returns 404 when off |
| `features.service_appointments` | bool | true | same, `/service/appointments*` endpoints |
| `features.custom_orders` | bool | true | same, `/custom-orders` endpoints |
| `features.reviews` | bool | true | model and dealership reviews |
| `features.favorites` | bool | true | favourites button and page |
| `demo.show_login_hint` | bool | false | shows where demo staff credentials live on the login page |
| `server.cors_origins` | list of origins | `["http://localhost:3000"]` | CORS (backend only) |
| `server.api_title` | string | `<name> API` | OpenAPI title (backend only) |

Backend container variables related to branding:

| Variable | Default | Purpose |
|---|---|---|
| `BRAND_DIR` | `/app/brands/demo` (image) | directory with `brand.yaml` and `assets/` |
| `BRAND_CONFIG_FILE` | `$BRAND_DIR/brand.yaml` | explicit path to the YAML |
| `BRAND__...` | - | override any field (see above) |
| `BRAND` (compose only) | `demo` | selects `./brands/<BRAND>` |
| `BRAND_DB_NAME` (compose only) | `POSTGRES_NAME` | separate database per brand for local demos |

### Catalog pack format (`catalog.yaml`)

Entities reference each other by name; names are the natural keys for upserts
(city = name + country, model = name + `production_year_start`, trim = model + name, vehicle = VIN).

```yaml
cities: [{ name: Grodno, country: Belarus }]
dealerships:
  - { name: Toyota Grodno, city: Grodno, country: Belarus, address: "...", phone_number: "+375...", email: grodno@example.com }
body_types: [Sedan, Crossover, Pickup]
engines: [{ name: 2.5 Hybrid, fuel_type: hybrid, horsepower: 218 }]        # gasoline|diesel|electric|hybrid|lpg
transmissions: [{ name: e-CVT, type: cvt, number_of_gears: 1 }]           # automatic|manual|cvt|dct
features: [{ name: Toyota Safety Sense, description: "..." }]
models:
  - name: RAV4
    body_type: Crossover
    production_year_start: 2023
    features: [Toyota Safety Sense]
    trims: [{ name: 2.5 Hybrid AWD-i, engine: 2.5 Hybrid, transmission: e-CVT, drive_type: AWD }]  # FWD|RWD|AWD
vehicles:
  - { vin: JTMW43FV20D000005, model: RAV4, trim: 2.5 Hybrid AWD-i, dealership: Toyota Grodno, production_year: 2024, exterior_color: Khaki, price: 156000 }
```

Quote values that contain commas inside `{ ... }` flow mappings. Not covered by packs: the service catalog and spare parts
seeded by migration `0001_baseline` (generic, Russian names) - edit them through the staff UI/API.

## API overview

All API routes are under `/api/v1` (see `src/api/v1/router.py`).

Primary routers:

- `/auth` (signup/signin/refresh/logout)
- `/health`
- `/users`, `/customers`
- `/cities`, `/dealerships` (+ `/dealerships/{id}/media`, `/dealerships/{id}/reviews`)
- `/models`, `/features`, `/vehicles`
- `/orders`, `/custom-orders`
- `/reviews`, `/test-drives`, `/favorites`
- `/logs` (audit logs + reports)
