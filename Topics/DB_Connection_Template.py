# MetaData is used to store database schema information.
# Here we will use it to set a default schema name for all tables.
from sqlalchemy import MetaData

# Async SQLAlchemy components for asynchronous database operations.
from sqlalchemy.ext.asyncio import (
    AsyncSession,       # Async version of SQLAlchemy Session
    async_sessionmaker, # Factory used to create AsyncSession objects
    create_async_engine # Creates an asynchronous database engine
)

# Base class used for all ORM models (User, Todo, Product, etc.)
from sqlalchemy.orm import DeclarativeBase


# Database connection string
# Format:
# postgresql+asyncpg://username:password@host:port/database_name
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/todo_db"


# Default PostgreSQL schema name
# Tables will be created inside TODO_S schema
DEFAULT_SCHEMA_NAME = "TODO_S"


# MetaData object holds information about tables, constraints, schema, etc.
# Setting schema here means every model inheriting Base
# will automatically use this schema.
metadata = MetaData(
    schema=DEFAULT_SCHEMA_NAME
)


# Base class for all ORM models
#
# Example:
# class Todo(Base):
#     __tablename__ = "todo1"
#
# Every model should inherit from Base.
class Base(DeclarativeBase):
    metadata = metadata


# Engine represents the actual connection to the database.
#
# echo=True
#   -> Prints SQL queries in terminal.
#
# future=True
#   -> Enables SQLAlchemy 2.0 style behavior.
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True
)


# Session Factory
#
# bind=engine
#   -> Attach session to our PostgreSQL engine.
#
# class_=AsyncSession
#   -> Every session created will be an AsyncSession.
#
# expire_on_commit=False
#   -> Objects remain accessible after commit.
#
# Example:
# db = local_maker()
local_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Dependency Injection Function
#
# FastAPI uses this function whenever a database session is required.
#
# Example:
# @app.get("/")
# async def get_todos(db: AsyncSession = Depends(get_db)):
#     ...
#
# Flow:
# 1. Create session
# 2. Yield session to API
# 3. Automatically close session after request completes
async def get_db():
    async with local_maker() as session:
        yield session



#---------------------------------------------------------------------------------------------------=
#                   DB models : 
#---------------------------------------------------------------------------------------------------=

from sqlalchemy.orm import mapped_column,Mapped

from sqlalchemy import column,Boolean,String,Uuid,DateTime
from datetime import datetime
from uuid import UUID,uuid4

class TodoModel(Base):
    __classname__="Todo1",
    __table_args__={"schema"=DEFAULT_SCHEMA_NAME}
    id:Mapped[Uuid]=mapped_column(
        Uuid,
        default=uuid4,
        primary_key=True,
        index=True
    )
    name
