from alembic import context

from database import engine
from models import Base


if context.is_offline_mode():
    context.configure(url=engine.url.render_as_string(hide_password=False),
                      target_metadata=Base.metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata,
                          render_as_batch=connection.dialect.name == "sqlite")
        with context.begin_transaction():
            context.run_migrations()
