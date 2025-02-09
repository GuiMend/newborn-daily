import uuid

from pydantic import EmailStr
from sqlmodel import Field, SQLModel
from sqlalchemy import event
from app.database import TimestampMixin, update_timestamp


class UserBase(SQLModel):
    username: str | None = Field(default=None, max_length=50)
    email: EmailStr = Field(unique=True, max_length=50)
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)


class User(UserBase, TimestampMixin, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    password: str = Field(max_length=255)


class UserResponse(UserBase):
    id: uuid.UUID


class UserCreate(UserBase):
    password: str


event.listen(User, "before_update", update_timestamp)
