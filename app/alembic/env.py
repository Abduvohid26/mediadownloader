from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
import asyncio

# Alembic konfiguratsiyasi
config = context.config
# Logging sozlamalari
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from database.database import Base
from models.user import User
target_metadata = Base.metadata

def run_migrations_offline():
    # Offline rejimda migratsiyalarni bajarish
    url = config.get_main_option("sqlalchemy.url")
    print(url, 'ur;')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    # Online rejimda migratsiyalarni bajarish
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        echo=True,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
