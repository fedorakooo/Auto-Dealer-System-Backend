-- Local development only: wipes everything, including schema_migrations, so the app re-applies all migrations.
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
