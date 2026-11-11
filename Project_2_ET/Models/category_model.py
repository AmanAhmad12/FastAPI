from uuid import UUID, uuid4

from sqlalchemy import String, Uuid, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from config.db import Base, DEFAULT_SCHEMA_NAME


class CategoryModel(Base):
    __tablename__ = "categories"
    __table_args__ = {"schema": DEFAULT_SCHEMA_NAME}

    category_id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
        index=True
    )

    category_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{DEFAULT_SCHEMA_NAME}.users.user_id"),
        nullable=False
    )