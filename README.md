# Flowguard — Condition-Based Predictive Maintenance Platform

> **Project:** Condition-Based Predictive Maintenance for KPC Pipeline Pump Infrastructure  
> **Team:** NULL_TERMINATORS (KPC Cohort, Inuka Fellowship, Power Learn Project)  
> **Target Asset:** Kenya Pipeline Company (KPC) 1,342 km multi-product pipeline network (PS1 Mombasa to PS13 Kisumu)

---

## 1. Executive Summary & Operational Background

The **Flowguard** backend platform is a multi-tenant, condition-based predictive maintenance engine engineered for high-pressure fluid transport pipeline networks. 

### Team NULL_TERMINATORS
The team placed first in Hackathon 1 by building a revenue reconciliation pipeline addressing billing discrepancies in KPC's order-to-cash process. This capstone extends that reconciliation and data pipeline methodology to operational infrastructure: preventing unplanned pump failures across KPC's pipeline network.

| Member | Role | Key Responsibilities |
| :--- | :--- | :--- |
| **Silas Kibet** | Data Engineering Lead | Medallion pipeline (Bronze/Silver/Gold), synthetic data generation, ETL |
| **Brian Kioko** | Modelling & Machine Learning Lead | Feature engineering, HDI physics engine, 7-day risk classifier, RUL regression |
| **Ingrid Miriam** | Dashboard & Visualisation Lead | Dashboarding, stakeholder views, metric visualizations |
| **Eugene Obunde** | Storytelling & ROI Lead | Executive narrative, financial ROI, business case documentation |
| **Lameck Mugo** | QA & Documentation Lead | Testing, UAT notes, deployment readiness, security verification |

---

## 2. The Problem & Business Value

### The KPC Operational Problem
Kenya Pipeline Company (KPC) operates 1,342 kilometres of pipeline connecting Mombasa, Nairobi, Nakuru, Eldoret, and Kisumu, transporting over 14 billion litres of petroleum products annually. Traditional maintenance relies on calendar-based servicing:
1. **Unnecessary Overhauls:** Fully operational pumps are taken offline for scheduled servicing, incurring unnecessary downtime and maintenance expenditure.
2. **Undetected Degradation:** Mechanical wear (bearing friction, seal breakdown, impeller cavitation) develops between fixed maintenance intervals. Catastrophic failures have historical precedent—such as 400,000 litres lost at Thange River (2015) and 551,000 litres at Kiboko (2018), valued at over KES 63 million in product loss, environmental cleanup, and throughput stoppages.

### The Flowguard Solution & ROI
Flowguard transitions KPC to continuous, condition-driven risk mitigation:
- **Continuous Telemetry Ingestion:** Sub-minute streaming of pump vibration, temperatures, suction/discharge pressures, and electrical metrics.
- **Physics-Informed Anomaly Detection:** Real-time calculation of **Pressure Residuals** against manufacturer-rated head curves to derive a **Health Deviation Index (HDI)**.
- **7-Day Risk Classification:** ML models evaluate progressive mechanical wear to predict failures within a 7-day window and classify fault modes (`bearing_fault`, `impeller_wear`, `seal_leak`, `normal`).
- **Remaining Useful Life (RUL):** Regression models estimate remaining operational hours with Monte Carlo Dropout confidence interval bounds.
- **Explainability (XAI):** SHAP feature attributions isolate the specific sub-assembly (Bearing, Impeller, Seal, Motor) driving risk.
- **Closed-Loop Action:** Risk scores $\ge 70\%$ trigger automated condition-based work orders, while scheduled maintenance across the fleet is prioritized dynamically by RUL.

---

## 3. Technology Stack & Architectural Principles

- **Core Framework:** Python 3.13, FastAPI, Pydantic v2
- **ORM & Database:** SQLAlchemy 2.0 (Multi-Schema: `master`, `bronze`, `silver`, `gold`), Alembic, PostgreSQL 16 (with SQLite in-memory fallback for testing)
- **Security:** Multi-tenant JWT auth (`X-Tenant-ID` scoping), bcrypt password hashing
- **Code Quality & Testing:** Pytest, pytest-cov, Ruff, `uv` / standard `venv`

```
                          ┌──────────────────────────┐
                          │   SCADA / Sensor Stream  │
                          └─────────────┬────────────┘
                                        │
                                        ▼
    ┌───────────────────────────────────────────────────────────────────────┐
    │                        Medallion Data Pipeline                        │
    │  ┌──────────────────┐    ┌───────────────────┐    ┌────────────────┐  │
    │  │  Bronze Schema   │───►│   Silver Schema   │───►│  Gold Schema   │  │
    │  │  (Raw Telemetry) │    │  (Quality Gate)   │    │(Rolling Aggs)  │  │
    │  └──────────────────┘    └───────────────────┘    └───────┬────────┘  │
    └───────────────────────────────────────────────────────────┼───────────┘
                                                                │
                                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                          Analytics, Physics & Machine Learning                          │
│  ┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────────┐  │
│  │ Flowguard Physics HDI │──►│ 7-Day Risk Classifier │──►│   RUL Regression Engine   │  │
│  │  (Pressure Residuals) │   │ (Fault Classification)│   │  (MC Dropout Confidence)  │  │
│  └───────────────────────┘   └───────────┬───────────┘   └─────────────┬─────────────┘  │
└──────────────────────────────────────────┼─────────────────────────────┼────────────────┘
                                           │                             │
                                           ▼                             ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              Operational Workflow Core                                  │
│  ┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────────┐  │
│  │   SHAP Explainability │   │ Auto Work Order Gen   │   │  RUL-Ranked Schedule      │  │
│  │ (Sub-component XAI)   │   │  (Trigger Risk >= 0.7)│   │   (Priority Re-Ranking)   │  │
│  └───────────────────────┘   └───────────────────────┘   └───────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Architectural Guardrails
1. **Strict One-Way Dependency:** `routes` $\rightarrow$ `services` $\rightarrow$ `models` $\rightarrow$ `database`.
2. **Vertical Slice Architecture:** Modular domain isolation under `app/<module>/` (`models.py`, `schemas.py`, `services.py`, `routes.py`).
3. **Mandatory Multi-Tenancy:** Every tenant-scoped entity inherits `TenantScopedMixin`. Queries are forced through `get_current_tenant_id` at dependency injection, preventing cross-tenant leakage.
4. **Separation of Reference Data from Telemetry:** Telemetry flows through `app/etl` (`bronze`, `silver`, `gold`), leaving master asset tables (`station`, `pump`, `tenant`) read-only to the pipeline.
5. **Zero Secrets in Code:** Configured strictly via `app/core/config.py` from `.env`.

---

## 4. System Layout & Modules

```
app/
├── core/                   # Config, DB session factory, JWT auth, tenancy mixins
├── tenant/                 # Multi-tenant configuration & alert threshold settings
├── user/                   # User authentication & RBAC (Admin, Engineer, Operator)
├── station/                # KPC station metadata, geographic coordinates & throughput
├── pump/                   # Pump inventory, rated specifications & status tracking
├── etl/                    # Medallion ETL pipeline: bronze -> silver -> gold -> simulator
├── feature_engineering/    # Gold layer & HDI transformation into model-ready feature vectors
├── flowgard_engine/        # Pressure residual calculation & Health Deviation Index (HDI)
├── prediction/             # 7-day failure risk classifier & fault mode categorization
├── rul/                    # Remaining Useful Life regression & MC Dropout confidence bounds
├── explainability/         # SHAP feature attributions & component risk allocation
├── alert/                  # Threshold alerts & operational escalation
├── work_order/             # Condition-based maintenance work orders & auto-generation
├── maintenance_schedule/   # RUL-ranked prioritised maintenance calendar
└── model_metrics/          # Model accuracy, precision, recall & confusion matrix storage
```

---

## 5. Medallion Data Pipeline & Telemetry Ingestion

Flowguard enforces a 3-tier **Medallion Data Architecture**:

1. **Bronze Layer (`bronze` schema):**
   - Raw, append-only landing area storing sub-minute SCADA telemetry, Open-Meteo weather API payloads, and regional threat indicators.
   - Tables: `bronze.pump_telemetry`, `bronze.weather_api`, `bronze.regional_risk`.
2. **Silver Layer (`silver` schema):**
   - Cleaned, quality-gated operational layer. Filters out invalid readings (e.g. `motor_current_amps <= 0`, `temperature_bearing_c > 200°C`).
   - Tables: `silver.sensor_reading`, `silver.weather_reading`, `silver.regional_risk_score`.
3. **Gold Layer (`gold` schema):**
   - Feature store computing rolling aggregations (3-reading window) per pump asset.
   - Metrics: `vibration_axial_rolling_avg`, `vibration_axial_rolling_std`, `temperature_bearing_rolling_avg`, `temperature_bearing_rolling_max`, `pressure_discharge_rolling_avg`.
   - Table: `gold.pump_features`.

---

## 6. KPC Fleet Specifications (13 Stations)

Flowguard is seeded with KPC's 13 pipeline booster and depot stations from Coast to Nyanza:

| Code | Station Name | Region | County | Throughput ($\text{m}^3/\text{day}$) |
| :--- | :--- | :--- | :--- | :--- |
| **PS1** | PS1 Mombasa | Coast | Mombasa | 3,200 |
| **PS2** | PS2 Samburu | Coast | Kwale | 3,200 |
| **PS3** | PS3 Maungu | Coast | Taita Taveta | 3,200 |
| **PS4** | PS4 Mtito Andei | Eastern | Kitui | 3,200 |
| **PS5** | PS5 Konza | Eastern | Machakos | 3,200 |
| **PS6** | PS6 Nairobi Depot | Nairobi | Nairobi | 4,000 |
| **PS7** | PS7 Naivasha | Rift Valley | Nakuru | 2,600 |
| **PS8** | PS8 Gilgil | Rift Valley | Nakuru | 2,600 |
| **PS9** | PS9 Nakuru | Rift Valley | Nakuru | 2,600 |
| **PS10**| PS10 Molo | Rift Valley | Nakuru | 2,600 |
| **PS11**| PS11 Eldoret Depot | Rift Valley | Uasin Gishu | 2,600 |
| **PS12**| PS12 Turbo | Rift Valley | Uasin Gishu | 2,000 |
| **PS13**| PS13 Kisumu Depot | Nyanza | Kisumu | 2,000 |

---

## 7. Quickstart & Deployment

Refer to [RUNBOOK.md](RUNBOOK.md) for complete environment setup instructions.

### Step 1: Environment Setup
```bash
# Clone repository & create local environment configuration
cp .env.example .env

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Database Setup & Seed
```bash
# Execute Alembic migrations to build multi-schema architecture
alembic upgrade head

# Seed KPC anchor tenant, stations, pumps, and administrative user
python scripts/seed_kpc_tenant.py
```

### Step 3: Run Sensor Telemetry Simulator (Optional)
```bash
# Generate live simulated SCADA sensor telemetry into Bronze layer
python scripts/run_simulator.py
```

### Step 4: Launch FastAPI Backend
```bash
uvicorn app.main:app --reload
```
- **Interactive Swagger Documentation:** `http://localhost:8000/docs`
- **ReDoc Documentation:** `http://localhost:8000/redoc`
- **Health Check Endpoint:** `http://localhost:8000/health`

---

## 8. Verification & Quality Assurance

Run the automated quality and test execution script:
```bash
./scripts/check.sh
```

The script runs two verification stages:
1. **Ruff Linter & Formatter Check:** Confirms code style compliance across all modules.
2. **Pytest Suite:** Runs all unit tests covering all 13 modules.

```
======================== 64 passed, 1 warning in 8.58s =========================
=== All checks passed! Repository is healthy and ready to push. ===
```

---

## 9. Primary API Endpoints Map

| Category | Endpoint | Method | Description |
| :--- | :--- | :--- | :--- |
| **System** | `/health` | `GET` | Service status and runtime diagnostics |
| **Tenants** | `/api/v1/tenants` | `GET`, `POST` | Manage tenant configurations & thresholds |
| **Users** | `/api/v1/users/login` | `POST` | Authenticate user & issue JWT bearer token |
| **Stations** | `/api/v1/stations` | `GET`, `POST` | KPC pump station metadata |
| **Pumps** | `/api/v1/pumps` | `GET`, `POST` | Pump inventory & rated pressure specs |
| **Engine** | `/api/v1/flowgard-engine/pumps/{id}/compute` | `POST` | Calculate Pressure Residual & HDI score |
| **Predictions**| `/api/v1/predictions/pumps/{id}/trigger` | `POST` | Run 7-day failure risk classifier |
| **RUL** | `/api/v1/rul/pumps/{id}/trigger` | `POST` | Estimate Remaining Useful Life & confidence bounds |
| **XAI** | `/api/v1/explainability/pumps/{id}/trigger` | `POST` | Calculate SHAP feature attributions |
| **Alerts** | `/api/v1/alerts` | `GET`, `POST` | Active threshold alerts & resolution |
| **Work Orders**| `/api/v1/work-orders` | `GET`, `POST` | Condition-based work order tracking |
| **Schedule** | `/api/v1/maintenance-schedule/rank` | `POST` | Re-rank maintenance calendar by RUL urgency |
| **Metrics** | `/api/v1/model-metrics` | `GET`, `POST` | Historical ML model benchmark metrics |
