from uuid import UUID,uuid4
from datetime import datetime

from sqlalchemy import column,Boolean,String,DateTime,Uuid,func
from pydantic import EmailStr,SecretStr

from sqlalchemy.orm import Mapped,mapped_column
from config.db import Base,DEFAULT_SCHEMA_NAME

class UserModel(Base):
    
    __tablename__="user"
    __table_args__={"schema":DEFAULT_SCHEMA_NAME}

    id:Mapped[UUID]=mapped_column(
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
    email:Mapped[str]=mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    password:Mapped[str]=mapped_column(
        String(200),
        nullable=False
    )
    refresh_token:Mapped[str|None]=mapped_column(
        String(200),
        nullable=True
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
