from sqlalchemy import String, DateTime, Uuid, func,Uuid,Float,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from config.db import Base, DEFAULT_SCHEMA_NAME
from uuid import UUID, uuid4
from datetime import datetime


class ExpenseModel(Base):
    __tablename__="expenses"
    __table_args__={"schema":DEFAULT_SCHEMA_NAME}

    expense_id:Mapped[UUID]=mapped_column(
        Uuid,
        default=uuid4,
        primary_key=True,
        index=True
    )
    user_id:Mapped[UUID]=mapped_column(
        ForeignKey(f"{DEFAULT_SCHEMA_NAME}.users.user_id"),
        nullable=False
    )
    category_id:Mapped[UUID]=mapped_column(
        ForeignKey(f"{DEFAULT_SCHEMA_NAME}.categories.category_id"),
        nullable=False
    )
    amount:Mapped[float]=mapped_column(
        Float,
        default=0.0,
        index=True
    )
    description:Mapped[str]=mapped_column(
        String(200),
        nullable=False,
        index=True
    )
    payment_method:Mapped[str]=mapped_column(
        String(200),
        nullable=False,
        index=True
    )
    expense_date:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
