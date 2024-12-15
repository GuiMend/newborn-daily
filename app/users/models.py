from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from app.database import TimestampModel


class UserBase(SQLModel):
    username: str | None = Field(default=None, max_length=50)
    email: EmailStr = Field(primary_key=True)
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)


class User(UserBase, TimestampModel, table=True):
    password: str = Field(max_length=100)


class UserResponse(UserBase):
    pass


class UserCreate(UserBase):
    password: str
