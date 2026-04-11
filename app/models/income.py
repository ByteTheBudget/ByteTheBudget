from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import date

class IncomeBase(SQLModel):
    source: str
    amount: float
    type: str
    date_received: date
    user_id: int = Field(foreign_key="user.id")

class Income(IncomeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)