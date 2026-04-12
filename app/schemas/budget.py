from sqlmodel import SQLModel
from typing import Optional


class BudgetCreate(SQLModel):
    category_id: int
    limit: float


class BudgetUpdate(SQLModel):
    limit: float


class BudgetResponse(SQLModel):
    id: int
    category_id: int
    limit: float
    user_id: int