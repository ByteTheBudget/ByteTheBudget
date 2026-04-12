from app.repositories.subscription import SubscriptionRepository
from app.repositories.subscription_template import SubscriptionTemplateRepository
from app.models.subscription import SubscriptionBase
from datetime import date

class SubscriptionService:
    def __init__(self, subscription_repo: SubscriptionRepository, template_repo: SubscriptionTemplateRepository = None):
        self.subscription_repo = subscription_repo
        self.template_repo = template_repo

    def get_all_subscriptions(self, user_id: int):
        return self.subscription_repo.get_all_by_user(user_id)

    def get_subscription_by_id(self, subscription_id: int):
        return self.subscription_repo.get_by_id(subscription_id)

    def get_monthly_total(self, user_id: int) -> float:
        return self.subscription_repo.get_total_monthly_by_user(user_id)

    def get_upcoming_renewals(self, user_id: int):
        return self.subscription_repo.get_upcoming_renewals(user_id)

    def create_subscription(self, user_id: int, name: str, amount: float, billing_cycle: str, next_renewal: date):
        subscription_data = SubscriptionBase(
            name=name,
            amount=amount,
            billing_cycle=billing_cycle,
            next_renewal=next_renewal,
            user_id=user_id
        )
        return self.subscription_repo.create(subscription_data)

    def create_from_template(self, user_id: int, template_id: int, next_renewal: date):
        if not self.template_repo:
            raise Exception("Template repository not provided")
        template = self.template_repo.get_by_id(template_id)
        if not template:
            raise Exception("Template not found")
        return self.create_subscription(
            user_id=user_id,
            name=template.name,
            amount=template.default_amount,
            billing_cycle=template.billing_cycle,
            next_renewal=next_renewal
        )

    def update_subscription(self, subscription_id: int, name: str, amount: float, billing_cycle: str, next_renewal: date, is_active: bool):
        return self.subscription_repo.update(subscription_id, name, amount, billing_cycle, next_renewal, is_active)

    def delete_subscription(self, subscription_id: int):
        return self.subscription_repo.delete(subscription_id)