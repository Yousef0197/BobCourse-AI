import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models so Alembic can detect them for autogenerate
from app.db.base import Base  # noqa: F401, E402
import app.models  # noqa: F401, E402 — registers all 15 ORM models

target_metadata = Base.metadata

# Override the sqlalchemy.url from the DATABASE_URL environment variable when present.
# The alembic.ini has a sensible localhost default; CI/Docker will set DATABASE_URL.
_env_db_url = os.environ.get("DATABASE_URL")
if _env_db_url:
    # Normalise postgresql:// → postgresql+psycopg:// for psycopg3
    if _env_db_url.startswith("postgresql://") and "+psycopg" not in _env_db_url:
        _env_db_url = _env_db_url.replace("postgresql://", "postgresql+psycopg://", 1)
    config.set_main_option("sqlalchemy.url", _env_db_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
