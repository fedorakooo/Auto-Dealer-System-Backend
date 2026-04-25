# Auto-Dealer-System-Backend

Project backend for an auto dealership system: user authentication, role-based access (customer/employee/admin), catalog management (cities/dealerships/models/vehicles), sales flows (orders and custom orders), customer activity (reviews, favorites, test drives), and an audit/logging subsystem.

## Contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Architecture and repository structure](#architecture-and-repository-structure)
- [Configuration](#configuration)
- [How to run](#how-to-run)
- [Database initialization](#database-initialization)
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

## API overview

All API routes are under `/api/v1` (see `src/api/v1/router.py`).

Primary routers:

- `/auth` (signup/signin/refresh/logout)
- `/health`
- `/users`, `/customers`
- `/cities`, `/dealerships`
- `/models`, `/features`, `/vehicles`
- `/orders`, `/custom-orders`
- `/reviews`, `/test-drives`, `/favorites`
- `/logs` (audit logs + reports)
