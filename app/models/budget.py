from sqlmodel import Field, SQLModel
from typing import Optional

class BudgetBase(SQLModel):
    limit: float
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")

class Budget(BudgetBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)