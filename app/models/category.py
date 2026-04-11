from sqlmodel import Field, SQLModel
from typing import Optional

class CategoryBase(SQLModel):
    name: str = Field(index=True, unique=True)
    is_default: bool = Field(default=True)

class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)