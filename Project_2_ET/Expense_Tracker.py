from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy import text

# Import all routers
from Routers import (
    categorys,
    income,
    expense,
    budget,
    report
)
from Routers.users import users

# Import all models so SQLAlchemy can register them
from Models import (
    UserModel,
    CategoryModel,
    IncomeModel,
    ExpenseModel,
    BudgetModel
)

from config.db import (
    DEFAULT_SCHEMA_NAME,
    Base,
    engine
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application Started")

    # Create schema and tables
    async with engine.begin() as conn:

        await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{DEFAULT_SCHEMA_NAME}"'))
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Close database connection pool
    await engine.dispose()

    print("Application Closed")


# FastAPI App
app = FastAPI(
    title="Expense Tracker",
    description="Expense Tracker That Tracks All Expenses",
    version="1.0.0",
    lifespan=lifespan
)

# All routers
routes = [
    users,
    categorys,
    income,
    expense,
    budget,
    report
]

# Add /api prefix to all routers
for route in routes:
    app.include_router(router=route,prefix="/api")


    