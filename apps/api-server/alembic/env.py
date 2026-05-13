from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from app.config.settings import get_settings
import app.core.database
import app.core.database_models

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = app.core.database.Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

settings = get_settings()
SQLALCHEMY_DATABASE_URL = f"mysql+mysqldb://{settings.MYSQL_USERNAME}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_BINDING_PORT}/{settings.MYSQL_DATABASE}"
url = SQLALCHEMY_DATABASE_URL

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    def include_object(object, name, type_, reflected, compare_to):
        """
        FK로 자동 생성된 인덱스는 autogenerate에서 무시
        MySQL은 FK 생성 시 자동으로 인덱스를 만들기 때문에
        모델에 명시되지 않은 FK 인덱스는 비교하지 않음
        """
        # FK 컬럼의 자동 생성 인덱스 무시
        if type_ == "index" and reflected and compare_to is None:
            # 데이터베이스에는 있지만 모델에는 없는 인덱스
            # FK로 자동 생성된 인덱스일 가능성이 높음
            return False
        return True

    # Override the sqlalchemy.url in config with our constructed URL
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
