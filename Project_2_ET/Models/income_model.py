from sqlalchemy import (
    String,
    DateTime,
    Uuid,
    Float,
    ForeignKey,
    func
)
from sqlalchemy.orm import Mapped, mapped_column

from config.db import Base, DEFAULT_SCHEMA_NAME

from uuid import UUID, uuid4
from datetime import datetime


class IncomeModel(Base):
    __tablename__ = "incomes"
    __table_args__ = {"schema": DEFAULT_SCHEMA_NAME}

    income_id: Mapped[UUID] = mapped_column(
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

    source: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0
    )

    description: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    income_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )