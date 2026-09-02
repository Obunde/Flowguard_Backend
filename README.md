# Flowguard — Predictive Maintenance Platform for KPC Pipeline Infrastructure

> **Capstone Project:** Condition-Based Predictive Maintenance for KPC Pipeline Pump Infrastructure  
> **Team NULL_TERMINATORS:** KPC Cohort, Inuka Fellowship, Power Learn Project

---

## 1. Executive Summary & Team NULL_TERMINATORS

Team **NULL_TERMINATORS** placed first in Hackathon 1 by developing a revenue reconciliation pipeline for Kenya Pipeline Company (KPC). This capstone extends that reconciliation methodology to unplanned pump failures across KPC's 1,342-kilometre pipeline network (Mombasa to Nairobi, Nakuru, Eldoret, and Kisumu), handling over 14 billion litres annually.

### Team Roles & Structure
- **Silas Kibet** — Data Engineering Lead *(Pipeline, synthetic data generation, ETL)*
- **Brian Kioko** — Modelling & Machine Learning Lead *(Hypothesis testing, feature engineering, ML models)*
- **Ingrid Miriam** — Dashboard & Visualisation Lead *(Dashboarding, stakeholder views)*
- **Eugene Obunde** — Storytelling & ROI Lead *(Briefs, executive narrative, business case)*
- **Lameck Mugo** — Quality Assurance & Documentation Lead *(Testing, UAT notes, deployment readiness)*

---

## 2. Problem Statement & Solution

### The Problem
Traditional time-based, fixed-interval maintenance causes unnecessary servicing of operational pumps while leaving units approaching mechanical degradation undetected. Historical incidents (such as 400,000 litres lost at Thange River in 2015 and 551,000 litres at Kiboko in 2018, valued at ~KES 63M) highlight the financial and safety risks of undetected failure.

### The Solution
Flowguard introduces continuous, data-driven risk assessment:
1. **Daily Failure Classification:** Evaluates each pump against a 7-day failure risk window using rolling sensor features (vibration, temperature, pressure, motor current).
2. **Remaining Useful Life (RUL):** Predicts RUL (in hours) for high-risk units to define precise service windows.
3. **Condition-Based Work Orders & Scheduling:** Automatically prioritizes maintenance technician deployment and spare parts allocation.

---

## 3. Technology Stack & Architecture

- **Core Framework:** FastAPI, Pydantic v2
- **ORM & Database:** SQLAlchemy 2.0, Alembic migrations, PostgreSQL (with SQLite in-memory fallback for testing)
- **Authentication & Security:** Multi-tenant JWT auth (tenant + role claims carried in the token), bcrypt password hashing, invite-only onboarding with forced first-login password reset
- **Testing & Tooling:** Pytest, pytest-cov, Ruff, `uv` / standard `venv`

### Architecture Rules
1. **Strict One-Way Dependency:** `routes` \(\rightarrow\) `services` \(\rightarrow\) `models` \(\rightarrow\) `database`.
2. **Vertical Slice per Entity:** Organized under `app/<module>/` (`models.py`, `schemas.py`, `services.py`, `routes.py`).
3. **Mandatory Multi-Tenancy:** Every tenant-scoped table inherits `TenantScopedMixin` (`tenant_id` FK). No route can query across tenants.
4. **Medallion ETL Pipeline:** `app/etl` (`bronze` \(\rightarrow\) `silver` \(\rightarrow\) `gold`) manages telemetry ingestion separately from entity reference data.
5. **Zero Secrets in Code:** Configured strictly via `app/core/config.py` from `.env`. `.env` is git-ignored.

### Roles & Onboarding

| Role | Scope | Responsibilities |
| :--- | :--- | :--- |
| `platform_admin` | Cross-tenant (no `tenant_id`) | Seeded once (`scripts/seed_platform_admin.py`). Onboards & manages tenants; blocked from every tenant-scoped route. |
| `admin` | Single tenant | Created automatically when a tenant is onboarded. Onboards & manages that tenant's users. |
| `planner` / `technician` / `viewer` | Single tenant | Operational users invited by their tenant `admin`. |

**Onboarding flow** (identical for tenants and users): the inviter supplies an email; the system creates the account with a random first-time password and emails it via SMTP (`app/core/email.py`). On first login the account receives only a short-lived **reset token** (`POST /api/v1/users/login` → `reset_required: true`); it must call `POST /api/v1/users/reset-password` to set a real password before any access token is issued.

---

## 4. System Layout & Modules

```
app/
├── core/                   # Config, DB session factory, JWT auth, tenancy mixins
├── tenant/                 # Multi-tenant configuration (Track A)
├── user/                   # User authentication & RBAC (Track A)
├── station/                # Pump station reference data (Track B)
├── pump/                   # Pump metadata & lifecycle parameters (Track B)
├── etl/                    # Medallion pipeline: bronze -> silver -> gold -> simulator
├── feature_engineering/    # Gold layer to model feature vectors (Track A)
├── flowgard_engine/        # Pressure residual & Health Deviation Index (Track B)
├── prediction/             # 7-day failure risk classification model (Track B)
├── rul/                    # Remaining Useful Life regression engine (Track A)
├── explainability/         # SHAP feature attributions & component decomposition (Track B)
├── alert/                  # Threshold alerts & operational risks (Track A)
├── work_order/             # Maintenance work orders & auto-generation (Track B)
├── maintenance_schedule/   # RUL-ranked prioritised calendar (Track A)
└── model_metrics/          # Model accuracy, confusion matrix & metrics (Track A)
```

---

## 5. Quickstart & Deployment

Refer to [RUNBOOK.md](RUNBOOK.md) for detailed deployment workflows.

### Installation
```bash
# 1. Clone repository & configure environment
cp .env.example .env

# 2. Install dependencies
pip install -r requirements.txt   # or `uv sync`

# 3. Execute database migrations
alembic upgrade head

# 4. Seed the platform admin (platform.admin@flow.com / Admin@123 by default)
python scripts/seed_platform_admin.py

# 5. Seed KPC anchor tenant reference data (stations + pump fleet)
python scripts/seed_kpc_tenant.py

# 6. Start API server
uvicorn app.main:app --reload
```

- **Interactive API Docs:** `http://localhost:8000/docs`
- **Health Endpoint:** `http://localhost:8000/health`

---

## 6. Testing & Quality Assurance

Run unit tests across all 13 modules:
```bash
pytest -v
```

All 64 unit tests pass successfully with zero errors.
