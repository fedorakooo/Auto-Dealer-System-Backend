import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import asyncpg

MIGRATIONS_DIR = Path(__file__).resolve().parents[3] / "db" / "migrations"
MIGRATION_FILE_PATTERN = re.compile(r"^(?P<version>\d{4})_(?P<name>[a-z0-9_]+)\.sql$")
LOCK_QUERY = "SELECT pg_advisory_lock(hashtext('auto_dealer_schema_migrations'))"
UNLOCK_QUERY = "SELECT pg_advisory_unlock(hashtext('auto_dealer_schema_migrations'))"

# Rows written by the previous heuristic migrator; together they equal the current baseline.
LEGACY_MIGRATION_NAMES = frozenset(
    {
        "legacy_19_table_baseline",
        "extended_34_table_architecture",
        "history_backfill_and_integrity_guards",
    }
)
BASELINE_VERSION = 1
BASELINE_MARKER_TABLES = frozenset({"users", "vehicles", "orders", "outbox_events"})


@dataclass(frozen=True)
class Migration:
    """SQL migration file with its version and checksum."""

    version: int
    name: str
    sql: str
    checksum: str


def load_migrations(directory: Path | None = None) -> tuple[Migration, ...]:
    """Loads migration files from the directory ordered by version."""
    migrations: list[Migration] = []
    for path in sorted((directory or MIGRATIONS_DIR).glob("*.sql")):
        match = MIGRATION_FILE_PATTERN.match(path.name)
        if match is None:
            raise ValueError(f"Invalid migration file name: {path.name}")
        sql = path.read_text(encoding="utf-8")
        checksum = hashlib.sha256(sql.replace("\r\n", "\n").encode("utf-8")).hexdigest()
        migrations.append(Migration(int(match["version"]), match["name"], sql, checksum))
    versions = [migration.version for migration in migrations]
    if len(versions) != len(set(versions)):
        raise ValueError("Duplicate migration versions found")
    return tuple(migrations)


async def _ensure_migrations_table(connection: asyncpg.Connection) -> None:
    await connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    await connection.execute("ALTER TABLE schema_migrations ADD COLUMN IF NOT EXISTS checksum VARCHAR(64)")


async def _adopt_existing_database(connection: asyncpg.Connection, applied: dict[int, asyncpg.Record]) -> None:
    """Register databases created before file-based migrations existed as already at the baseline."""
    legacy_names = {row["name"] for row in applied.values() if row["name"] in LEGACY_MIGRATION_NAMES}
    if legacy_names:
        if legacy_names != LEGACY_MIGRATION_NAMES:
            raise RuntimeError(
                f"Database has a partially applied legacy schema ({sorted(legacy_names)}); fix it manually"
            )
        async with connection.transaction():
            await connection.execute("DELETE FROM schema_migrations WHERE name = ANY($1::text[])", list(legacy_names))
            await connection.execute(
                "INSERT INTO schema_migrations(version, name) VALUES ($1, 'baseline')", BASELINE_VERSION
            )
        return
    if applied:
        return
    rows = await connection.fetch("SELECT tablename FROM pg_tables WHERE schemaname = current_schema()")
    if {row["tablename"] for row in rows} >= BASELINE_MARKER_TABLES:
        await connection.execute(
            "INSERT INTO schema_migrations(version, name) VALUES ($1, 'baseline')", BASELINE_VERSION
        )


async def migrate(connection: asyncpg.Connection, migrations_dir: Path | None = None) -> list[int]:
    """Applies pending migrations and returns the versions applied."""
    migrations = load_migrations(migrations_dir)
    await connection.execute(LOCK_QUERY)
    try:
        await _ensure_migrations_table(connection)
        rows = await connection.fetch("SELECT version, name, checksum FROM schema_migrations")
        await _adopt_existing_database(connection, {row["version"]: row for row in rows})
        rows = await connection.fetch("SELECT version, name, checksum FROM schema_migrations")
        applied = {row["version"]: row for row in rows}

        for migration in migrations:
            row = applied.get(migration.version)
            if row is not None and row["checksum"] not in (None, migration.checksum):
                raise RuntimeError(
                    f"Migration {migration.version:04d}_{migration.name} was modified after it was applied; "
                    "add a new migration instead"
                )

        newly_applied: list[int] = []
        for migration in migrations:
            if migration.version in applied:
                continue
            async with connection.transaction():
                await connection.execute(migration.sql)
                await connection.execute(
                    "INSERT INTO schema_migrations(version, name, checksum) VALUES ($1, $2, $3)",
                    migration.version,
                    migration.name,
                    migration.checksum,
                )
            newly_applied.append(migration.version)
        return newly_applied
    finally:
        await connection.execute(UNLOCK_QUERY)
