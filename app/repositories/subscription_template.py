from sqlmodel import Session, select
from app.models.subscription_template import SubscriptionTemplate, SubscriptionTemplateBase
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class SubscriptionTemplateRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, template_data: SubscriptionTemplateBase) -> SubscriptionTemplate:
        try:
            template = SubscriptionTemplate.model_validate(template_data)
            self.db.add(template)
            self.db.commit()
            self.db.refresh(template)
            return template
        except Exception as e:
            logger.error(f"Error creating subscription template: {e}")
            self.db.rollback()
            raise

    def get_all(self) -> list[SubscriptionTemplate]:
        return self.db.exec(select(SubscriptionTemplate)).all()

    def get_by_id(self, template_id: int) -> Optional[SubscriptionTemplate]:
        return self.db.get(SubscriptionTemplate, template_id)

    def update(self, template_id: int, name: str, default_amount: float, billing_cycle: str) -> SubscriptionTemplate:
        template = self.db.get(SubscriptionTemplate, template_id)
        if not template:
            raise Exception("Template not found")
        try:
            template.name = name
            template.default_amount = default_amount
            template.billing_cycle = billing_cycle
            self.db.add(template)
            self.db.commit()
            self.db.refresh(template)
            return template
        except Exception as e:
            logger.error(f"Error updating subscription template: {e}")
            self.db.rollback()
            raise

    def delete(self, template_id: int):
        template = self.db.get(SubscriptionTemplate, template_id)
        if not template:
            raise Exception("Template not found")
        try:
            self.db.delete(template)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error deleting subscription template: {e}")
            self.db.rollback()
            raise