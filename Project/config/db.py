# Import MetaData class
# MetaData stores information about schemas, tables, columns, constraints, etc.
from sqlalchemy import MetaData


# Import asynchronous SQLAlchemy components

# AsyncSession:
# Represents a database session that supports async/await
#
# async_sessionmaker:
# Factory used to create AsyncSession objects
#
# create_async_engine:
# Creates an asynchronous database engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)


# DeclarativeBase is the parent class for creating ORM models
#
# Example:
#
# class Todo(Base):
#     ...
#
from sqlalchemy.orm import DeclarativeBase


# Database connection URL
#
# postgresql+asyncpg
#   └── PostgreSQL database using asyncpg driver
#
# user
#   └── PostgreSQL username
#
# password
#   └── PostgreSQL password
#
# localhost
#   └── PostgreSQL server host
#
# 5432
#   └── PostgreSQL default port
#
# todo_db
#   └── Database name
DATABASE_URL = (
    "postgresql+asyncpg://user:password@localhost:5432/todo_db"
)


# Custom schema name
#
# PostgreSQL Structure:
#
# todo_db
#   └── TODO_S
#       └── todos
#
DEFAULT_SCHEMA_NAME = "TODO_S"


# Create metadata object
#
# All ORM models inheriting from Base
# will automatically use schema "TODO_S"
metadata = MetaData(
    schema=DEFAULT_SCHEMA_NAME
)


# Base Class
#
# Every SQLAlchemy model should inherit from Base
#
# Example:
#
# class Todo(Base):
#     __tablename__ = "todos"
#
class Base(DeclarativeBase):

    # Attach custom metadata
    # so all tables are created inside TODO_S schema
    metadata = metadata


# Create Async Database Engine
#
# Engine is responsible for:
# - Creating DB connections
# - Managing connection pool
# - Sending SQL queries
# - Handling transactions
#
engine = create_async_engine(

    # PostgreSQL connection URL
    DATABASE_URL,

    # Prints generated SQL queries in terminal
    #
    # Useful during development/debugging
    echo=True,
    future=True # it ensure the sqlalchemy  2.x behaviour 
)


# Session Factory
#
# Instead of creating sessions manually every time,
# AsyncSessionLocal creates them for us.
#
# Think:
#
# AsyncSessionLocal
#         ↓
# Creates
#         ↓
# AsyncSession
#
AsyncSessionLocal = async_sessionmaker(

    # Engine to be used by the session
    bind=engine,

    # Session class to create
    class_=AsyncSession,

    # Prevent objects from becoming inactive
    # after a commit operation
    #
    # Without this:
    #   todo.title
    # may require a DB reload after commit
    expire_on_commit=False
)


# FastAPI Dependency
#
# This function provides a database session
# to API routes.
#
# Example:
#
# @app.get("/")
# async def home(
#     db: AsyncSession = Depends(get_db)
# ):
#     pass
#
async def get_db():

    # Create database session
    async with AsyncSessionLocal() as session:

        # Give session to FastAPI route
        yield session

    # After request completion,
    # session is automatically closed.