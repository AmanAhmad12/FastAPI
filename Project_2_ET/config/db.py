    from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from sqlalchemy.orm import DeclarativeBase


DEFAULT_SCHEMA_NAME = "EXPENSE_TRACKER"

DATABASE_URL = (
    "postgresql+asyncpg://user:password@localhost:5432/Expense_Tracker_DB"
)

metadata = MetaData(
    schema=DEFAULT_SCHEMA_NAME
)


class Base(DeclarativeBase):
    metadata = metadata


engine = create_async_engine(
    DATABASE_URL,
    echo=True
)

sessionBuilder = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    async with sessionBuilder() as session:
        yield session