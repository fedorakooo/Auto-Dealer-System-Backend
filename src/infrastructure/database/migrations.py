from dataclasses import dataclass
from pathlib import Path

import asyncpg

EXTENDED_OBJECTS = frozenset(
    {
        "employment_status",
        "vehicle_lifecycle_status",
        "payment_method",
        "payment_status",
        "service_appointment_status",
        "service_order_status",
        "outbox_event_status",
        "employee_profiles",
        "customer_addresses",
        "vehicle_status_history",
        "vehicle_price_history",
        "order_payments",
        "order_status_history",
        "test_drive_status_history",
        "service_catalog",
        "service_appointments",
        "service_orders",
        "service_order_items",
        "spare_parts",
        "dealership_part_inventory",
        "outbox_events",
        "idempotency_keys",
    }
)

OPERATIONAL_MARKERS = frozenset(
    {
        "record_vehicle_price_history",
        "record_order_status_history",
        "record_test_drive_status_history",
        "enforce_order_payment_total",
        "refresh_service_order_total",
        "insert into vehicle_price_history",
        "insert into vehicle_status_history",
        "insert into order_status_history",
        "insert into test_drive_status_history",
        "insert into service_catalog",
        "insert into spare_parts",
        "insert into dealership_part_inventory",
    }
)


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    statements: tuple[str, ...]


def _split_sql(source: str) -> tuple[str, ...]:
    statements: list[str] = []
    current: list[str] = []
    in_dollar_quote = False
    index = 0
    while index < len(source):
        if source.startswith("$$", index):
            in_dollar_quote = not in_dollar_quote
            current.append("$$")
            index += 2
            continue
        character = source[index]
        current.append(character)
        if character == ";" and not in_dollar_quote:
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
        index += 1
    remainder = "".join(current).strip()
    if remainder:
        statements.append(remainder)
    return tuple(statements)


def load_migrations(schema_path: Path | None = None) -> tuple[Migration, ...]:
    path = schema_path or Path(__file__).resolve().parents[3] / "db" / "sql" / "01-schema.sql"
    statements = _split_sql(path.read_text(encoding="utf-8"))
    baseline: list[str] = []
    extension: list[str] = []
    operational: list[str] = []
    for statement in statements:
        normalized = statement.lower()
        if any(marker in normalized for marker in OPERATIONAL_MARKERS):
            target = operational
        elif any(name in normalized for name in EXTENDED_OBJECTS):
            target = extension
        else:
            target = baseline
        target.append(statement)
    return (
        Migration(1, "legacy_19_table_baseline", tuple(baseline)),
        Migration(2, "extended_34_table_architecture", tuple(extension)),
        Migration(3, "history_backfill_and_integrity_guards", tuple(operational)),
    )


async def migrate(connection: asyncpg.Connection, schema_path: Path | None = None) -> list[int]:
    await connection.execute("SELECT pg_advisory_lock(hashtext('auto_dealer_schema_migrations'))")
    try:
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        applied_rows = await connection.fetch("SELECT version FROM schema_migrations")
        applied_versions = {row["version"] for row in applied_rows}
        if not applied_versions:
            table_rows = await connection.fetch("SELECT tablename FROM pg_tables WHERE schemaname = current_schema()")
            existing_tables = {row["tablename"] for row in table_rows}
            legacy_tables = {
                "users",
                "customers",
                "cities",
                "dealerships",
                "body_types",
                "engines",
                "transmissions",
                "models",
                "features",
                "model_features",
                "vehicles",
                "orders",
                "custom_orders",
                "custom_order_features",
                "vehicle_media",
                "model_media",
                "favorites",
                "reviews",
                "test_drive_requests",
            }
            extended_tables = {
                name
                for name in EXTENDED_OBJECTS
                if name
                not in {
                    "employment_status",
                    "vehicle_lifecycle_status",
                    "payment_method",
                    "payment_status",
                    "service_appointment_status",
                    "service_order_status",
                    "outbox_event_status",
                }
            }
            if legacy_tables <= existing_tables:
                await connection.execute(
                    "INSERT INTO schema_migrations(version, name) VALUES (1, 'legacy_19_table_baseline')"
                )
                applied_versions.add(1)
            if extended_tables <= existing_tables:
                await connection.execute(
                    "INSERT INTO schema_migrations(version, name) VALUES (2, 'extended_34_table_architecture')"
                )
                applied_versions.add(2)
        newly_applied: list[int] = []
        for migration in load_migrations(schema_path):
            if migration.version in applied_versions:
                continue
            transaction = connection.transaction()
            await transaction.start()
            try:
                for statement in migration.statements:
                    await connection.execute(statement)
                await connection.execute(
                    "INSERT INTO schema_migrations(version, name) VALUES ($1, $2)",
                    migration.version,
                    migration.name,
                )
            except Exception:
                await transaction.rollback()
                raise
            else:
                await transaction.commit()
                newly_applied.append(migration.version)
        return newly_applied
    finally:
        await connection.execute("SELECT pg_advisory_unlock(hashtext('auto_dealer_schema_migrations'))")
