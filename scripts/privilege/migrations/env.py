import os
import sys
from logging.config import fileConfig
from pathlib import Path
from typing import TYPE_CHECKING

from alembic import context as _context
from sqlalchemy import engine_from_config, pool

if TYPE_CHECKING:
    from alembic.runtime.environment import EnvironmentContext


context: "EnvironmentContext" = _context  # type:ignore
FILE_PATH = Path(__file__).absolute()


config = context.config


def _getDB(path: Path):
    path = Path(__file__).absolute().parent
    while "main.py" not in os.listdir(path):
        path = path.parent
    sys.path.append(str(path))
    os.chdir(path)
    from utils.db import db  # noqa:E402

    return db


db = _getDB(FILE_PATH)
config.set_main_option("sqlalchemy.url", str(db.config["dsn"]).replace("%", "%%"))
target_metadata = db

os.chdir(FILE_PATH.parent.parent)

fileConfig(config.config_file_name)


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
