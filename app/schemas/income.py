from sqlmodel import SQLModel
from datetime import date
from typing import Optional


class IncomeCreate(SQLModel):
    source: str
    amount: float
    type: str
    date_received: date


class IncomeUpdate(SQLModel):
    source: Optional[str] = None
    amount: Optional[float] = None
    type: Optional[str] = None
    date_received: Optional[date] = None


class IncomeResponse(SQLModel):
    id: int
    source: str
    amount: float
    type: str
    date_received: date
    user_id: int