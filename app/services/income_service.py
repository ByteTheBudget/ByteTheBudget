from app.repositories.income import IncomeRepository
from app.models.income import IncomeBase
from datetime import date

class IncomeService:
    def __init__(self, income_repo: IncomeRepository):
        self.income_repo = income_repo

    def get_all_income(self, user_id: int):
        return self.income_repo.get_all_by_user(user_id)

    def get_income_by_id(self, income_id: int):
        return self.income_repo.get_by_id(income_id)

    def create_income(self, user_id: int, source: str, amount: float, type: str, date_received: date):
        income_data = IncomeBase(
            source=source,
            amount=amount,
            type=type,
            date_received=date_received,
            user_id=user_id
        )
        return self.income_repo.create(income_data)

    def get_monthly_total(self, user_id: int, month: int, year: int) -> float:
        return self.income_repo.get_total_by_user_and_month(user_id, month, year)

    def update_income(self, income_id: int, source: str, amount: float, type: str, date_received: date):
        return self.income_repo.update(income_id, source, amount, type, date_received)

    def delete_income(self, income_id: int):
        return self.income_repo.delete(income_id)
