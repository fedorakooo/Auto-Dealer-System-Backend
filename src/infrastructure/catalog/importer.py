"""Idempotent upsert of a catalog pack into PostgreSQL (one transaction)."""

from dataclasses import dataclass, field

import asyncpg

from src.infrastructure.catalog.schema import CatalogPack


@dataclass
class ImportStats:
    """Number of upserted rows per table."""

    counts: dict[str, int] = field(default_factory=dict)

    def add(self, table: str, n: int = 1) -> None:
        """Adds n upserted rows for the table."""
        self.counts[table] = self.counts.get(table, 0) + n


async def _upsert_by_name(
    conn: asyncpg.Connection, table: str, key_sql: str, key: tuple[object, ...], columns: dict[str, object]
) -> int:
    """Updates the row matching key_sql or inserts it; returns its id. Fields absent from the pack are kept."""
    row_id = await conn.fetchval(f"SELECT id FROM {table} WHERE {key_sql}", *key)
    if row_id is None:
        names = list(columns)
        placeholders = ", ".join(f"${i}" for i in range(1, len(names) + 1))
        return await conn.fetchval(
            f"INSERT INTO {table} ({', '.join(names)}) VALUES ({placeholders}) RETURNING id", *columns.values()
        )
    provided = {name: value for name, value in columns.items() if value is not None}
    assignments = ", ".join(f"{n} = ${i}" for i, n in enumerate(provided, start=2))
    await conn.execute(f"UPDATE {table} SET {assignments} WHERE id = $1", row_id, *provided.values())
    return row_id


async def import_catalog(conn: asyncpg.Connection, pack: CatalogPack) -> ImportStats:
    """Upserts the whole pack in one transaction and returns per-table counts."""
    stats = ImportStats()
    async with conn.transaction():
        city_ids: dict[tuple[str, str], int] = {}
        for c in pack.cities:
            city_ids[(c.name, c.country)] = await conn.fetchval(
                "INSERT INTO cities (name, country) VALUES ($1, $2) "
                "ON CONFLICT (name, country) DO UPDATE SET name = EXCLUDED.name RETURNING id",
                c.name,
                c.country,
            )
            stats.add("cities")

        dealership_ids: dict[str, int] = {}
        for d in pack.dealerships:
            dealership_ids[d.name] = await _upsert_by_name(
                conn,
                "dealerships",
                "name = $1",
                (d.name,),
                {
                    "name": d.name,
                    "address": d.address,
                    "city_id": city_ids[(d.city, d.country)],
                    "phone_number": d.phone_number,
                    "email": d.email,
                    "opening_hours": d.opening_hours,
                    "latitude": d.latitude,
                    "longitude": d.longitude,
                    "description": d.description,
                },
            )
            stats.add("dealerships")

        body_type_ids: dict[str, int] = {}
        for name in pack.body_types:
            body_type_ids[name] = await conn.fetchval(
                "INSERT INTO body_types (name) VALUES ($1) "
                "ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name RETURNING id",
                name,
            )
            stats.add("body_types")

        engine_ids: dict[str, int] = {}
        for e in pack.engines:
            engine_ids[e.name] = await _upsert_by_name(
                conn, "engines", "name = $1", (e.name,), e.model_dump(mode="python")
            )
            stats.add("engines")

        transmission_ids: dict[str, int] = {}
        for t in pack.transmissions:
            transmission_ids[t.name] = await conn.fetchval(
                "INSERT INTO transmissions (name, type, number_of_gears) VALUES ($1, $2, $3) "
                "ON CONFLICT (name) DO UPDATE SET type = EXCLUDED.type, number_of_gears = EXCLUDED.number_of_gears "
                "RETURNING id",
                t.name,
                t.type.value,
                t.number_of_gears,
            )
            stats.add("transmissions")

        feature_ids: dict[str, int] = {}
        for f in pack.features:
            feature_ids[f.name] = await conn.fetchval(
                "INSERT INTO features (name, description) VALUES ($1, $2) "
                "ON CONFLICT (name) DO UPDATE SET description = COALESCE(EXCLUDED.description, features.description) "
                "RETURNING id",
                f.name,
                f.description,
            )
            stats.add("features")

        trim_ids: dict[tuple[str, str], tuple] = {}
        for m in pack.models:
            model_id = await conn.fetchval(
                "INSERT INTO models (name, body_type_id, model_code, is_in_production, production_year_start, "
                "number_of_seats, description) VALUES ($1, $2, $3, $4, $5, $6, $7) "
                "ON CONFLICT (name, production_year_start) DO UPDATE SET body_type_id = EXCLUDED.body_type_id, "
                "model_code = COALESCE(EXCLUDED.model_code, models.model_code), "
                "is_in_production = EXCLUDED.is_in_production, "
                "number_of_seats = COALESCE(EXCLUDED.number_of_seats, models.number_of_seats), "
                "description = COALESCE(EXCLUDED.description, models.description) RETURNING id",
                m.name,
                body_type_ids[m.body_type],
                m.model_code,
                m.is_in_production,
                m.production_year_start,
                m.number_of_seats,
                m.description,
            )
            stats.add("models")
            for feature in m.features:
                await conn.execute(
                    "INSERT INTO model_features (model_id, feature_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                    model_id,
                    feature_ids[feature],
                )
            for t in m.trims:
                trim_id = await conn.fetchval(
                    "INSERT INTO trims (model_id, name, engine_id, transmission_id, drive_type, max_speed_kmh, "
                    "acceleration_0_100_sec) VALUES ($1, $2, $3, $4, $5, $6, $7) "
                    "ON CONFLICT (model_id, name) DO UPDATE SET engine_id = EXCLUDED.engine_id, "
                    "transmission_id = EXCLUDED.transmission_id, "
                    "drive_type = COALESCE(EXCLUDED.drive_type, trims.drive_type), "
                    "max_speed_kmh = COALESCE(EXCLUDED.max_speed_kmh, trims.max_speed_kmh), "
                    "acceleration_0_100_sec = "
                    "COALESCE(EXCLUDED.acceleration_0_100_sec, trims.acceleration_0_100_sec) "
                    "RETURNING id",
                    model_id,
                    t.name,
                    engine_ids[t.engine],
                    transmission_ids[t.transmission],
                    t.drive_type.value if t.drive_type else None,
                    t.max_speed_kmh,
                    t.acceleration_0_100_sec,
                )
                trim_ids[(m.name, t.name)] = (model_id, trim_id)
                stats.add("trims")

        for v in pack.vehicles:
            model_id, trim_id = trim_ids[(v.model, v.trim)]
            inserted = await conn.fetchval(
                "INSERT INTO vehicles (model_id, trim_id, dealership_id, vin, production_year, exterior_color, "
                "interior_color, price) VALUES ($1, $2, $3, $4, $5, $6, $7, $8) "
                "ON CONFLICT (vin) DO NOTHING RETURNING id",
                model_id,
                trim_id,
                dealership_ids[v.dealership],
                v.vin,
                v.production_year,
                v.exterior_color,
                v.interior_color,
                v.price,
            )
            stats.add("vehicles" if inserted else "vehicles_skipped_existing")

        await conn.execute(
            "INSERT INTO dealership_part_inventory "
            "(dealership_id, part_id, quantity, reserved_quantity, reorder_level) "
            "SELECT d.id, p.id, 10, 0, 3 FROM dealerships d CROSS JOIN spare_parts p "
            "ON CONFLICT (dealership_id, part_id) DO NOTHING"
        )
    return stats
