# This file contains the database configuration and session management
from datetime import datetime, timezone
from typing import Annotated
from fastapi import Depends
from sqlmodel import Field, create_engine, Session

from app.config import settings

DB_USERNAME = settings.db_username
DB_PASSWORD = settings.db_password
DB_HOSTNAME = settings.db_hostname
DB_PORT = settings.db_port
DB_NAME = settings.db_name

DATABASE_URL = (
    f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    # Perhaps not needed with Alembic (?)
    # SQLModel.metadata.create_all(engine)
    pass


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


class TimestampMixin:
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # created_at: datetime | None = Field(
    #     default=None,
    #     sa_column=Column(
    #         DateTime,
    #         nullable=False,
    #         server_default=func.now(),
    #     ),
    # )
    # updated_at: datetime | None = Field(
    #     default=None,
    #     sa_column=Column(
    #         DateTime,
    #         nullable=False,
    #         server_default=func.now(),
    #         onupdate=func.now(),
    #     ),
    # )


def update_timestamp(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)
