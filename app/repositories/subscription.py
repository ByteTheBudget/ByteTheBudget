from sqlmodel import Session, select, func
from app.models.subscription import Subscription, SubscriptionBase
from typing import Optional
from datetime import date
import logging

logger = logging.getLogger(__name__)

class SubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, subscription_data: SubscriptionBase) -> Subscription:
        try:
            subscription = Subscription.model_validate(subscription_data)
            self.db.add(subscription)
            self.db.commit()
            self.db.refresh(subscription)
            return subscription
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            self.db.rollback()
            raise

    def get_all_by_user(self, user_id: int) -> list[Subscription]:
        return self.db.exec(
            select(Subscription).where(Subscription.user_id == user_id)
        ).all()

    def get_active_by_user(self, user_id: int) -> list[Subscription]:
        return self.db.exec(
            select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.is_active == True
            )
        ).all()

    def get_by_id(self, subscription_id: int) -> Optional[Subscription]:
        return self.db.get(Subscription, subscription_id)

    def get_total_monthly_by_user(self, user_id: int) -> float:
        subscriptions = self.get_active_by_user(user_id)
        total = 0.0
        for sub in subscriptions:
            if sub.billing_cycle == "yearly":
                total += sub.amount / 12
            else:
                total += sub.amount
        return total

    def get_upcoming_renewals(self, user_id: int, days: int = 30) -> list[Subscription]:
        from datetime import timedelta
        today = date.today()
        upcoming = today + timedelta(days=days)
        return self.db.exec(
            select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.is_active == True,
                Subscription.next_renewal <= upcoming
            ).order_by(Subscription.next_renewal)
        ).all()

    def update(self, subscription_id: int, name: str, amount: float, billing_cycle: str, next_renewal: date, is_active: bool) -> Subscription:
        subscription = self.db.get(Subscription, subscription_id)
        if not subscription:
            raise Exception("Subscription not found")
        try:
            subscription.name = name
            subscription.amount = amount
            subscription.billing_cycle = billing_cycle
            subscription.next_renewal = next_renewal
            subscription.is_active = is_active
            self.db.add(subscription)
            self.db.commit()
            self.db.refresh(subscription)
            return subscription
        except Exception as e:
            logger.error(f"Error updating subscription: {e}")
            self.db.rollback()
            raise

    def delete(self, subscription_id: int):
        subscription = self.db.get(Subscription, subscription_id)
        if not subscription:
            raise Exception("Subscription not found")
        try:
            self.db.delete(subscription)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error deleting subscription: {e}")
            self.db.rollback()
            raise