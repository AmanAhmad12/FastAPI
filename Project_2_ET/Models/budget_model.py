from sqlalchemy import (
    String,
    Float,
    Boolean,
    Date,
    Uuid,
    ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column

from config.db import Base, DEFAULT_SCHEMA_NAME

from uuid import UUID, uuid4
from datetime import date


class BudgetModel(Base):
    __tablename__ = "budgets"
    __table_args__ = {"schema": DEFAULT_SCHEMA_NAME}

    budget_id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
        index=True
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{DEFAULT_SCHEMA_NAME}.users.user_id"),
        nullable=False,
        index=True
    )

    category_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{DEFAULT_SCHEMA_NAME}.categories.category_id"),
        nullable=False,
        index=True
    )

    budget_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    budget_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    spent_amount: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False
    )

    remaining_amount: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )