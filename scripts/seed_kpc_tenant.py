"""Seed KPC (Kenya Pipeline Company) as tenant #1, with its 13 pump stations
(PS1 Mombasa -> PS13 Kisumu Depot) and a starter pump fleet.

Idempotent: safe to run multiple times — looks up by slug/code/tag_number
before inserting.

NOTE on data provenance: there is no prototype snapshot file in this repo
yet (the scaffold task referenced one, but it wasn't present at scaffold
time), so the station list below is representative placeholder data laid
out along the real Mombasa - Nairobi - Nakuru - Eldoret - Kisumu pipeline
corridor (approximate town coordinates), not verified KPC asset records.
Replace STATIONS/pump generation below with real figures when available.

Usage:
    python scripts/seed_kpc_tenant.py
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session  # noqa: E402

from app.core.db import SessionLocal  # noqa: E402
from app.pump.models import Pump, PumpStatus  # noqa: E402
from app.station.models import Station  # noqa: E402
from app.tenant.models import Tenant  # noqa: E402

KPC_TENANT = {
    "name": "Kenya Pipeline Company",
    "slug": "kpc",
    "fluid_type": "petroleum_products",
    "pressure_threshold_kpa": 4500.0,
    "vibration_threshold_mm_s": 7.1,
    "branding_display_name": "KPC",
    "branding_primary_color": "#006633",
}

# code, name, region, county, lat, lon, commissioned_on, throughput capacity (m3/day)
STATIONS: list[tuple[str, str, str, str, float, float, date, float]] = [
    ("PS1", "PS1 Mombasa", "Coast", "Mombasa", -4.0225, 39.6086, date(1978, 1, 1), 3200.0),
    ("PS2", "PS2 Samburu", "Coast", "Kwale", -4.1667, 39.2000, date(1978, 1, 1), 3200.0),
    ("PS3", "PS3 Maungu", "Coast", "Taita Taveta", -3.5500, 38.7667, date(1978, 1, 1), 3200.0),
    ("PS4", "PS4 Mtito Andei", "Eastern", "Kitui", -2.6858, 38.1706, date(1978, 1, 1), 3200.0),
    ("PS5", "PS5 Konza", "Eastern", "Machakos", -1.7357, 37.1287, date(1978, 1, 1), 3200.0),
    ("PS6", "PS6 Nairobi Depot", "Nairobi", "Nairobi", -1.3192, 36.9278, date(1978, 1, 1), 4000.0),
    ("PS7", "PS7 Naivasha", "Rift Valley", "Nakuru", -0.7167, 36.4333, date(1994, 1, 1), 2600.0),
    ("PS8", "PS8 Gilgil", "Rift Valley", "Nakuru", -0.4903, 36.3178, date(1994, 1, 1), 2600.0),
    ("PS9", "PS9 Nakuru", "Rift Valley", "Nakuru", -0.3031, 36.0800, date(1994, 1, 1), 2600.0),
    ("PS10", "PS10 Molo", "Rift Valley", "Nakuru", -0.2500, 35.7333, date(1994, 1, 1), 2600.0),
    (
        "PS11",
        "PS11 Eldoret Depot",
        "Rift Valley",
        "Uasin Gishu",
        0.5143,
        35.2698,
        date(1994, 1, 1),
        2600.0,
    ),
    ("PS12", "PS12 Turbo", "Rift Valley", "Uasin Gishu", 0.6500, 35.0833, date(1994, 1, 1), 2000.0),
    ("PS13", "PS13 Kisumu Depot", "Nyanza", "Kisumu", -0.0917, 34.7680, date(1994, 1, 1), 2000.0),
]

PUMP_MANUFACTURERS = ("Sulzer", "KSB", "Flowserve")


def seed(db: Session) -> Tenant:
    tenant = db.query(Tenant).filter(Tenant.slug == KPC_TENANT["slug"]).one_or_none()
    if tenant is None:
        tenant = Tenant(**KPC_TENANT)
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        print(f"created tenant {tenant.slug} ({tenant.id})")
    else:
        print(f"tenant {tenant.slug} already exists ({tenant.id})")

    for idx, (code, name, region, county, lat, lon, commissioned_on, capacity) in enumerate(
        STATIONS
    ):
        station = (
            db.query(Station)
            .filter(Station.tenant_id == tenant.id, Station.code == code)
            .one_or_none()
        )
        if station is None:
            station = Station(
                tenant_id=tenant.id,
                code=code,
                name=name,
                region=region,
                county=county,
                latitude=lat,
                longitude=lon,
                commissioned_on=commissioned_on,
                throughput_capacity_m3_per_day=capacity,
            )
            db.add(station)
            db.commit()
            db.refresh(station)
            print(f"  created station {station.code} — {station.name}")
        else:
            print(f"  station {station.code} already exists")

        # Starter pump fleet: two mainline pumps per station.
        for p in (1, 2):
            tag_number = f"{code}-P{p:02d}"
            pump = (
                db.query(Pump)
                .filter(Pump.tenant_id == tenant.id, Pump.tag_number == tag_number)
                .one_or_none()
            )
            if pump is not None:
                print(f"    pump {tag_number} already exists")
                continue
            pump = Pump(
                tenant_id=tenant.id,
                station_id=station.id,
                tag_number=tag_number,
                manufacturer=PUMP_MANUFACTURERS[(idx + p) % len(PUMP_MANUFACTURERS)],
                model_number=f"HZ-{300 + idx * 10 + p}",
                install_date=commissioned_on,
                design_life_years=25,
                prior_intervention_count=0,
                rated_flow_m3_per_hour=round(capacity / 24, 2),
                rated_pressure_kpa=4200.0,
                status=PumpStatus.OPERATIONAL,
            )
            db.add(pump)
            print(f"    created pump {tag_number}")
        db.commit()

    return tenant


def main() -> None:
    db = SessionLocal()
    try:
        tenant = seed(db)
        station_count = db.query(Station).filter(Station.tenant_id == tenant.id).count()
        pump_count = db.query(Pump).filter(Pump.tenant_id == tenant.id).count()
        print(f"\nDone. KPC tenant {tenant.id}: {station_count} stations, {pump_count} pumps.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
