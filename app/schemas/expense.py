from sqlmodel import SQLModel
from datetime import date
from typing import Optional


class ExpenseCreate(SQLModel):
    description: str
    amount: float
    date: date
    category_id: int
    notes: Optional[str] = None


class ExpenseUpdate(SQLModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[date] = None
    category_id: Optional[int] = None
    notes: Optional[str] = None


class ExpenseResponse(SQLModel):
    id: int
    description: str
    amount: float
    date: date
    category_id: int
    notes: Optional[str] = None
    user_id: int