from sqlmodel import Field, SQLModel
from typing import Optional
from pydantic import EmailStr
from datetime import date


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    password: str
    role: str = ""
    is_active: bool = Field(default=True)
    joined_date: date = Field(default_factory=date.today)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)