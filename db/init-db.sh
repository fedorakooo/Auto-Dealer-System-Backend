#!/bin/bash
set -e

echo "Checking if database needs initialization..."

# Check if models table exists
TABLE_EXISTS=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h "localhost" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'models');" 2>/dev/null || echo "f")

if [ "$TABLE_EXISTS" = "t" ]; then
  echo "Database already initialized, skipping..."
  exit 0
fi

echo "Database not initialized, running DDL scripts..."

# Execute schema (DDL only)
echo "Executing 01-schema.sql..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h "localhost" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /docker-entrypoint-initdb.d/01-schema.sql

# Execute triggers and functions (DDL only)
for script in /docker-entrypoint-initdb.d/05-*.sql; do
  if [ -f "$script" ]; then
    echo "Executing $script"
    PGPASSWORD=$POSTGRES_PASSWORD psql -h "localhost" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$script"
  fi
done

echo "Database initialization completed!"
