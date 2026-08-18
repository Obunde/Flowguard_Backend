# app/etl — medallion ETL pipeline

Top-level module, deliberately separate from the entity modules (station,
pump, user, ...). This is the **only** part of the codebase allowed to write
`sensor_reading`, `weather_reading`, and `regional_risk_score` rows. It never
touches pump/station/user/tenant reference data — those flow the other
direction: entity modules are read-only inputs to ETL (e.g. gold-layer
aggregation needs to know which `pump_id`s exist), and reference data is
seeded independently (see `scripts/seed_kpc_tenant.py`), not produced here.

## Layers (bronze -> silver -> gold)

- `bronze/` — raw landing. Append-only, minimal validation. Lands sensor
  telemetry, weather API responses, and regional activity/risk source data
  more or less as received.
- `silver/` — cleaned, conformed. Reads bronze, writes the three canonical
  tables: `sensor_reading`, `weather_reading`, `regional_risk_score`.
- `gold/` — aggregated. Rolling-window feature computation over silver data
  (mean/std/min/max/trend per pump window, daily weather rollups, station
  risk composites). This is what `app/feature_engineering` reads.
- `simulator/` — continuous synthetic sensor-feed generator standing in for
  a real SCADA feed during development; writes into bronze like any other
  source.

This pass only scaffolds the tables and service signatures for each layer —
the actual cleaning/aggregation/generation logic is intentionally left as
`NotImplementedError` stubs to be filled in module by module.
