from app.repositories.subscription_template import SubscriptionTemplateRepository

class SubscriptionTemplateService:
    def __init__(self, template_repo: SubscriptionTemplateRepository):
        self.template_repo = template_repo

    def get_all_templates(self):
        return self.template_repo.get_all()

    def get_template_by_id(self, template_id: int):
        return self.template_repo.get_by_id(template_id)

    def create_template(self, name: str, default_amount: float, billing_cycle: str):
        from app.models.subscription_template import SubscriptionTemplateBase
        template_data = SubscriptionTemplateBase(
            name=name,
            default_amount=default_amount,
            billing_cycle=billing_cycle
        )
        return self.template_repo.create(template_data)

    def update_template(self, template_id: int, name: str, default_amount: float, billing_cycle: str):
        return self.template_repo.update(template_id, name, default_amount, billing_cycle)

    def delete_template(self, template_id: int):
        return self.template_repo.delete(template_id)
