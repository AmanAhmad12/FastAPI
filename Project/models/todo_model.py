from config.db import Base,DEFAULT_SCHEMA_NAME
from datetime import datetime
from uuid import UUID,uuid4
from sqlalchemy import column , String,Boolean,func,DateTime ,Uuid
from sqlalchemy.orm import mapped_column,Mapped


class TodoModel(Base):
    __tablename__= "todo1"
    __table_args__={"schema":DEFAULT_SCHEMA_NAME}
    id:Mapped[UUID] =mapped_column(
        Uuid,
        default=uuid4, 
        primary_key=True,
        index=True
    )
    name:Mapped[str]=mapped_column(
        String(200),
        nullable=False,
        index=True
    )
    category:Mapped[str]=mapped_column(

        String(150),
        nullable=False,
        index=True
    )
    status:Mapped[bool]=mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        server_default = func.now()
    )
    updated_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate = func.now()
    )