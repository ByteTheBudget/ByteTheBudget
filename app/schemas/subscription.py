from sqlmodel import SQLModel
from datetime import date
from typing import Optional


class SubscriptionCreate(SQLModel):
    name: str
    amount: float
    billing_cycle: str
    next_renewal: date


class SubscriptionFromTemplate(SQLModel):
    template_id: int
    next_renewal: date


class SubscriptionUpdate(SQLModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    billing_cycle: Optional[str] = None
    next_renewal: Optional[date] = None
    is_active: Optional[bool] = None


class SubscriptionResponse(SQLModel):
    id: int
    name: str
    amount: float
    billing_cycle: str
    next_renewal: date
    is_active: bool
    user_id: int