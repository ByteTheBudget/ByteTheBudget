from sqlmodel import SQLModel
from typing import Optional


class SubscriptionTemplateCreate(SQLModel):
    name: str
    default_amount: float
    billing_cycle: str


class SubscriptionTemplateUpdate(SQLModel):
    name: Optional[str] = None
    default_amount: Optional[float] = None
    billing_cycle: Optional[str] = None


class SubscriptionTemplateResponse(SQLModel):
    id: int
    name: str
    default_amount: float
    billing_cycle: str