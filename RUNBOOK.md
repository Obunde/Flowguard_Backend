# Flowguard Platform — Operations & Deployment Runbook

**Project Title:** Predictive Maintenance for Kenya Pipeline Company (KPC) Pump Infrastructure  
---

## 1. System Overview

Flowguard is a multi-tenant condition-based predictive maintenance backend for fluid-transport pipeline infrastructure (booster & depot stations, centrifugal pumps). The platform replaces fixed-interval servicing with continuous risk assessment and Remaining Useful Life (RUL) estimation.

---

## 2. Prerequisites & Environment Setup

### Prerequisites
- **Python:** Version 3.11+
- **Database:** PostgreSQL 14+ (or SQLite for local lightweight testing)
- **Package Manager:** `uv` (recommended) or `pip` / `venv`
- **Containerization:** Docker & Docker Compose (optional)

### Environment Configuration
1. Copy the template environment configuration file:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` to configure your local or production database parameters and secret keys:
   ```ini
   APP_NAME=flowgard
   ENVIRONMENT=development
   DEBUG=true
   DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/flowgard
   TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/flowgard_test
   JWT_SECRET_KEY=change-this-to-a-secure-random-secret-in-production
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
   CORS_ALLOW_ORIGINS=http://localhost:3000
   ```

> **Security Requirement:** Never commit `.env` or any production credential/key to git repository. `.env` is listed in `.gitignore`.

---

## 3. Installation & Database Setup

### Option A: Using `pip` & `venv`
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Alembic migrations to build schema
alembic upgrade head

# Seed the platform admin account (onboards tenants; not tenant-scoped)
python scripts/seed_platform_admin.py

# Seed KPC anchor tenant reference data (13 stations + pump fleet)
python scripts/seed_kpc_tenant.py
```

### Option B: Using `uv`
```bash
# Install dependencies into virtual environment
uv sync

# Run database migrations
uv run alembic upgrade head

# Seed the platform admin, then anchor tenant data
uv run python scripts/seed_platform_admin.py
uv run python scripts/seed_kpc_tenant.py
```

### Option C: Using Docker Compose
```bash
# Start PostgreSQL database and run migrations
docker compose up --build -d

# Run KPC seed script
docker compose --profile seed run --rm seed
```

---

## 4. Running the Application

### Development Server
Start the Uvicorn development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- **API Base Endpoint:** `http://localhost:8000`
- **Health Check:** `GET /health`
- **Interactive Swagger Documentation:** `http://localhost:8000/docs`
- **ReDoc Documentation:** `http://localhost:8000/redoc`

---

## 5. Testing & Verification

### Executing Unit & Integration Tests
Run pytest across all 13 modules:
```bash
pytest -v
```

To run tests with code coverage:
```bash
pytest --cov=app tests/
```

---

## 6. Architecture & API Module Structure

The backend architecture enforces vertical entity isolation and mandatory multi-tenancy (`tenant_id` scoping):

| Module | Track | Description | Key Endpoint Prefix |
| :--- | :--- | :--- | :--- |
| `tenant` | Track A | Tenant onboarding/branding/thresholds; platform-admin gated; creates the tenant's first `admin` | `/api/v1/tenants` |
| `user` | Track A | Invite-only user onboarding, roles, JWT login, forced first-login password reset | `/api/v1/users` |
| `station` | Track B | Pump station reference data (PS1–PS13) | `/api/v1/stations` |
| `pump` | Track B | Pump reference data & lifecycle metadata | `/api/v1/pumps` |
| `etl` | Shared | Medallion architecture (bronze/silver/gold) | Internal ETL |
| `feature_engineering` | Track A | Rolling-window feature vector construction | Internal service |
| `flowgard_engine` | Track B | Physics-based pressure residual & Health Deviation Index (HDI) | Internal computation |
| `prediction` | Track B | 7-day failure risk score & failure mode classification | `/api/v1/predictions` |
| `rul` | Track A | Remaining Useful Life (RUL) regression in hours | `/api/v1/rul` |
| `explainability` | Track B | SHAP feature attributions & component risk shares | `/api/v1/explainability` |
| `model_metrics` | Track A | Model performance metrics & confusion matrix | `/api/v1/model-metrics` |
| `alert` | Track A | Operational risk alerts & notification thresholding | `/api/v1/alerts` |
| `work_order` | Track B | Maintenance work order lifecycle & auto-generation | `/api/v1/work-orders` |
| `maintenance_schedule` | Track A | Prioritised RUL-based maintenance calendar | `/api/v1/maintenance-schedules` |

---

## 7. Operational Troubleshooting & Runbook Procedures

### Database Migration Rollback
If a database migration fails:
```bash
alembic downgrade -1
```

### Refreshing Seed Data
To reset local test data cleanly:
```bash
alembic downgrade base
alembic upgrade head
python scripts/seed_platform_admin.py
python scripts/seed_kpc_tenant.py
```

### Onboarding a Tenant and Its Users

1. Log in as the platform admin (`POST /api/v1/users/login`, default `platform.admin@flow.com` / `Admin@123`).
2. `POST /api/v1/tenants` with the tenant config plus `admin_email` / `admin_full_name`. This creates the tenant and its first `admin` user and emails that admin a first-time password (SMTP must be configured, or the call returns `503` with the tenant still created).
3. The tenant admin logs in with the emailed password → gets `reset_required: true` + a `reset_token` → `POST /api/v1/users/reset-password` to set a real password.
4. The tenant admin invites more users via `POST /api/v1/users` (`email`, `full_name`, `role`); each follows the same first-login reset flow.

### Pre-Commit Security Checklist
Before committing or pushing to GitHub:
1. Verify no `.env` file or secret credentials are stage-committed (`git status`).
2. Run unit tests (`pytest -v`).
3. Validate OpenAPI schema at `http://localhost:8000/docs`.
