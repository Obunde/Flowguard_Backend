# Flowgard Web — Predictive Maintenance

Flowgard Web is the Next.js control-room interface for the Flowguard predictive-maintenance platform. It presents backend-managed pump risk, station status, explainability, alerts, work orders, maintenance schedules, model metrics, tenant settings, and user administration.

Built with Next.js 16 App Router, React 19, TypeScript, and Tailwind CSS 4. The visual system follows the locally maintained `revenue-assurance` application: warm neutral surfaces, a compact dark sidebar, system typography, outline SVG icons, status-aware cards, and accessible tables.

## Recommended start: complete application

The frontend requires the FastAPI backend and PostgreSQL data. Start the complete application from the sibling backend repository:

```bash
cd ../Flowguard_Backend
docker compose up --build -d
docker compose ps
```

Open http://localhost:3000 and sign in with the default local demo account:

```text
Admin: admin@flowgard.com / Flowgard-UAT-2026!
Planner: planner@flowgard.com / Flowgard-UAT-2026!
Technician: technician@flowgard.com / Flowgard-UAT-2026!
Viewer: viewer@flowgard.com / Flowgard-UAT-2026!
```

API documentation is available at http://localhost:8000/docs.

Stop all services with:

```bash
cd ../Flowguard_Backend
docker compose down
```

See the backend repository README for configuration, SMTP setup, logs, database details, and data-reset instructions.

## Frontend-only development

Start the backend stack first, then run the Next.js development server separately. Stop the Compose frontend to release port 3000:

```bash
cd ../Flowguard_Backend
docker compose stop frontend

cd ../flowgard-web
npm ci
BACKEND_URL=http://localhost:8000 COOKIE_SECURE=false npm run dev
```

For a production build check:

```bash
npm run lint
npm run build
```

Do not run the frontend alone unless a compatible backend is reachable through `BACKEND_URL`. Authentication, dashboard loading, and all operational workflows depend on it.

## Application routes

| Route | Description |
| --- | --- |
| `/login` | Session login |
| `/` | Fleet overview, priority actions, network status, and model confidence |
| `/network` | Pipeline station network |
| `/pumps` | Filterable pump fleet and pump detail modal |
| `/flowgard` | HDI reconciliation engine and pump rankings |
| `/alerts` | Persisted alerts, acknowledgement, automation, and SMTP digest action |
| `/workorders` | Persisted work orders, status updates, and CSV export |
| `/schedule` | Persisted maintenance calendar, generation, and confirmation |
| `/model` | Classification and RUL model metrics |
| `/settings` | Tenant thresholds, branding, and capability status |
| `/admin` | Admin-only user management |

## Data flow and authentication

```text
Browser
  → Next.js route handlers (/api/auth and /api/backend)
  → FastAPI (/api/v1)
  → PostgreSQL
```

The frontend does not use `data/mockData.ts` at runtime. That file is retained as the source snapshot for the backend's idempotent demonstration bootstrap. Runtime station, pump, model, alert, work-order, schedule, settings, and user data come from FastAPI.

Access and refresh tokens are stored in HTTP-only cookies by the Next.js backend-for-frontend. When an API request receives `401`, the proxy attempts one refresh-token rotation and retries the request.

## Roles

- `admin`: tenant settings and user administration, plus operational actions
- `planner`: maintenance automation and operational planning actions
- `technician`: permitted work-order lifecycle actions
- `viewer`: read-only operational access

The UI renders navigation and actions from backend-issued effective permissions, while FastAPI remains the enforcement boundary for protected mutations.

The ROI page was intentionally removed: credible financial impact requires operator-specific cost, downtime, throughput, and intervention data. Flowgard does not present invented business-value claims. The bundled KPC-derived snapshot is demonstration data only; runtime tenancy, branding, thresholds, users, and assets are designed for any liquid-transport operator.

## Optional capabilities

The frontend reads `/api/v1/capabilities` and disables unavailable integrations instead of presenting false success notifications.

- Alert and schedule automation are available in the demo stack.
- SMTP digest delivery becomes available when backend `SMTP_*` settings are configured.
- Live SCADA ingestion and live model/RUL execution are not included in the supplied demo environment.

## Project structure

```text
app/                    App Router pages and BFF route handlers
components/layout/      Persistent application shell
components/ui/          Cards, badges, buttons, modal, toast, bars, and SVG icons
components/dashboard/   Dashboard visualizations
components/pumps/       Pump fleet interface
context/                Backend-fed application state and UI state
lib/api.ts              Dashboard aggregate adapter
lib/resources.ts        Typed operational resource client
data/types.ts           Shared frontend types
data/mockData.ts        Bootstrap source snapshot; not runtime state
```

## Troubleshooting

If the application does not open:

```bash
cd ../Flowguard_Backend
docker compose ps -a
docker compose logs --tail=100 api frontend bootstrap migrate
```

Common causes are occupied ports, an unsuccessful migration/bootstrap service, or starting Next.js without a reachable backend.
