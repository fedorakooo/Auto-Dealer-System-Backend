"""Imports a brand catalog pack: python -m src.cli.import_catalog <path/to/catalog.yaml> [--dry-run]."""

import argparse
import asyncio
import sys
from pathlib import Path

import asyncpg
import yaml
from pydantic import ValidationError

from src.config import settings
from src.infrastructure.catalog.importer import import_catalog
from src.infrastructure.catalog.schema import CatalogPack
from src.infrastructure.database.migrations import migrate


def load_pack(path: Path) -> CatalogPack:
    """Parses and validates a catalog pack YAML file."""
    with path.open(encoding="utf-8") as f:
        return CatalogPack.model_validate(yaml.safe_load(f) or {})


async def run(path: Path, dry_run: bool) -> int:
    """Validates and, unless dry_run, imports the pack; returns the exit code."""
    try:
        pack = load_pack(path)
    except (OSError, yaml.YAMLError, ValidationError) as exc:
        print(f"Invalid catalog pack {path}:\n{exc}", file=sys.stderr)
        return 1
    if dry_run:
        print(f"{path}: valid ({len(pack.models)} models, {len(pack.vehicles)} vehicles)")
        return 0

    pg = settings.postgres_settings
    conn = await asyncpg.connect(
        user=pg.POSTGRES_USER,
        password=pg.POSTGRES_PASSWORD,
        host=pg.POSTGRES_HOST,
        port=int(pg.POSTGRES_PORT),
        database=pg.POSTGRES_NAME,
    )
    try:
        await migrate(conn)
        stats = await import_catalog(conn, pack)
    finally:
        await conn.close()
    print(f"Imported {path}: " + ", ".join(f"{k}={v}" for k, v in sorted(stats.counts.items())))
    return 0


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="catalog.yaml of a brand pack")
    parser.add_argument("--dry-run", action="store_true", help="only validate the file")
    args = parser.parse_args()
    sys.exit(asyncio.run(run(args.path, args.dry_run)))


if __name__ == "__main__":
    main()
