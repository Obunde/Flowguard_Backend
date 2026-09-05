# Flowguard — Predictive Maintenance

Flowguard is a multi-tenant predictive-maintenance control room for pump infrastructure. It combines a FastAPI/PostgreSQL backend with a Next.js frontend for fleet risk monitoring, explainability, alerts, work orders, maintenance scheduling, model reporting, and administration.

The included demonstration tenant uses a KPC-derived dataset contains 13 stations and 35 pumps. Its sensor readings are synthetic and physics-informed; the displayed classification, RUL, model metrics, HDI, and SHAP values are imported from the prototype snapshot. Do not use demo data for operational decisions.

## Quick start

### Prerequisites

- Docker Engine with Docker Compose v2
- Ports `3000`, `8000`, and `5433` available

From this repository directory, start the complete stack:

```bash
docker compose up --build -d
docker compose ps
```

Compose starts the services in dependency order:

```text
PostgreSQL → Alembic migrations → demo bootstrap → FastAPI → Next.js
```

Open:

- Application: http://localhost:3000
- API documentation: http://localhost:8000/docs
- API health check: http://localhost:8000/health
- PostgreSQL from the host: `localhost:5433`

Default local demo credentials (when not overridden in `.env`):

```text
Admin: admin@flowgard.com / flowgard-demo
Planner: planner@flowgard.com / flowgard-planner
Technician: technician@flowgard.com / flowgard-technician
Viewer: viewer@flowgard.com / flowgard-viewer
```

These credentials are for local demonstration only. Override `SEED_ADMIN_EMAIL`, `SEED_ADMIN_PASSWORD`, and `JWT_SECRET_KEY` before using a shared or deployed environment.

Stop the stack:

```bash
docker compose down
```

To remove containers **and permanently delete the local PostgreSQL volume**:

```bash
docker compose down -v
```

## Configuration

Docker Compose has development defaults, so copying an environment file is optional for the first local run. For custom configuration:

```bash
cp .env.example .env
```

At minimum, review:

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`
- `JWT_REFRESH_TOKEN_EXPIRE_DAYS`
- `SEED_ADMIN_EMAIL`
- `SEED_ADMIN_PASSWORD`
- `CORS_ALLOW_ORIGINS`
- `SMTP_*` settings

If `SMTP_HOST` and `SMTP_FROM_EMAIL` are absent, Flowguard reports email digest delivery as unavailable and disables the digest action in the UI.

## Architecture

| Service | Responsibility |
| --- | --- |
| `db` | PostgreSQL 16 persistence |
| `migrate` | One-shot Alembic schema migration |
| `bootstrap` | Idempotent KPC snapshot and initial-admin import |
| `api` | FastAPI REST API on port 8000 |
| `frontend` | Next.js application on port 3000 |

Backend modules follow a vertical-slice structure:

```text
app/
├── auth_session/           # Login, refresh rotation, logout, current session
├── operations/             # Dashboard aggregates, capabilities, automation, digest, export
├── tenant/                 # Tenant configuration and branding
├── user/                   # User management and role-based access
├── station/                # Station reference data
├── pump/                   # Pump metadata
├── etl/                    # Bronze/silver/gold telemetry pipeline foundations
├── prediction/             # Persisted failure-risk predictions
├── rul/                    # Persisted remaining-useful-life estimates
├── explainability/         # SHAP and component attribution
├── alert/                  # Alert lifecycle
├── work_order/             # Work-order lifecycle and prediction-based generation
├── maintenance_schedule/   # Maintenance calendar
└── model_metrics/          # Model evaluation metrics
```

The browser communicates with Next.js route handlers. The Next.js backend-for-frontend stores access and refresh tokens in HTTP-only cookies, proxies requests to FastAPI, and rotates expired access sessions through the refresh endpoint.

## Available application features

- Authenticated dashboard and pump fleet
- Station network and pump detail views
- HDI, SHAP, component attribution, and model quality views
- Persisted alerts with generation and acknowledgement
- Persisted work orders with closing and CSV export
- Automatic maintenance schedule generation and confirmation
- Tenant settings
- Admin user creation, role assignment, enabling, and disabling
- Role-gated backend mutations
- SMTP alert digest when SMTP is configured

The `/api/v1/capabilities` endpoint is the source of truth for optional integrations. Live SCADA ingestion and live model/RUL inference are not supplied by the demo stack and are reported unavailable.

## Authentication and roles

Authentication endpoints:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

Supported roles are `admin`, `planner`, `technician`, and `viewer`. Tenant identity is derived from the signed access token; clients do not select tenants with an `X-Tenant-ID` header.

| Role | Read operations | Alerts | Work orders | Schedule | Models | Assets/tenant/users |
| --- | --- | --- | --- | --- | --- | --- |
| Admin | Yes | Manage | Manage | Manage | Run and manage | Manage |
| Planner | Yes | Manage | Manage | Manage | Run | No |
| Technician | Yes | Acknowledge/manage | Manage | Read | Read | No |
| Viewer | Yes | Read | Read/export | Read | Read | No |

Permissions are checked by FastAPI on every protected mutation. Active status and current role are revalidated from the database on each authenticated request, so disabling an account takes effect immediately.

## Useful commands

```bash
# Follow API and frontend logs
docker compose logs -f api frontend

# Re-run the idempotent demo bootstrap
docker compose run --rm bootstrap

# Rebuild after source changes
docker compose up --build -d

# Check service state
docker compose ps -a
```

## Local backend development

For backend-only development, configure `.env`, install dependencies, migrate PostgreSQL, bootstrap the demo data, and run Uvicorn:

```bash
uv sync
uv run alembic upgrade head
uv run python scripts/bootstrap_demo.py
uv run uvicorn app.main:app --reload
```

The bootstrap script reads `DEMO_SNAPSHOT_PATH`; its default expects the sibling frontend repository at `../flowgard-web/data/mockData.ts`.

## Quality checks

```bash
uv run ruff check app migrations scripts
uv run pytest -v
```

Test results can change as the project evolves; rely on the command output rather than a hardcoded test-count claim.

## Project context

Flowgard is tenant-neutral: the included KPC-derived data is a demonstration fixture, while tenant configuration, assets, users, thresholds, and operational records are isolated for deployment to any liquid-transport operator.
