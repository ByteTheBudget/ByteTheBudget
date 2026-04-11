from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import date

class SubscriptionBase(SQLModel):
    name: str
    amount: float
    billing_cycle: str
    next_renewal: date
    is_active: bool = Field(default=True)
    user_id: int = Field(foreign_key="user.id")

class Subscription(SubscriptionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)