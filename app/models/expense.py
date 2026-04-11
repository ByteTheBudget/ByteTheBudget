from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import date

class ExpenseBase(SQLModel):
    description: str
    amount: float
    date: date
    notes: Optional[str] = None
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")

class Expense(ExpenseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)