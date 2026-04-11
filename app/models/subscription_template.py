from sqlmodel import Field, SQLModel
from typing import Optional

class SubscriptionTemplateBase(SQLModel):
    name: str = Field(index=True, unique=True)
    default_amount: float
    billing_cycle: str

class SubscriptionTemplate(SubscriptionTemplateBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)