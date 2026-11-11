

    #    ####HOLD **** HOLD ***** HOLD   *****


from sqlalchemy import MetaData, Integer, String, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import asyncio

# Replace with your actual username/password
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/temp_db"

DEFAULT_SCHEMA_NAME = "PRACTICE"

# Engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True
)

# Session
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Metadata
metadata = MetaData(schema=DEFAULT_SCHEMA_NAME)


class Base(DeclarativeBase):
    metadata = metadata


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    age: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )


async def create_tables():
    async with engine.begin() as conn:

        # Create schema if not exists
        await conn.execute(
            text(f'CREATE SCHEMA IF NOT EXISTS "{DEFAULT_SCHEMA_NAME}"')
        )

        # Create tables
        await conn.run_sync(Base.metadata.create_all)

    print("Tables created successfully")


async def check_table():
    async with engine.connect() as conn:
        result = await conn.execute(
            text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'PRACTICE'
            """)
        )

        tables = result.fetchall()

        if tables:
            print("Tables Found:")
            for table in tables:
                print(table[0])
        else:
            print("No tables found")


async def main():
    await create_tables()
    await check_table()


asyncio.run(main())


