from sqlalchemy import String, DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column
from config.db import Base, DEFAULT_SCHEMA_NAME
from uuid import UUID, uuid4
from datetime import datetime


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": DEFAULT_SCHEMA_NAME}

    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
        index=True
    )

    user_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True
    )

    email: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        unique=True,
        index=True
    )

    password: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    role:Mapped[str]=mapped_column(
        String(100),
        nullable=False,
        default="USER"
    )

    refresh_token: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )