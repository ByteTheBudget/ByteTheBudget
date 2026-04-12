from app.repositories.expense import ExpenseRepository
from app.models.expense import ExpenseBase
from datetime import date
from typing import Optional

class ExpenseService:
    def __init__(self, expense_repo: ExpenseRepository):
        self.expense_repo = expense_repo

    def get_all_expenses(self, user_id: int):
        return self.expense_repo.get_all_by_user(user_id)

    def get_expense_by_id(self, expense_id: int):
        return self.expense_repo.get_by_id(expense_id)

    def get_recent_expenses(self, user_id: int, limit: int = 5):
        return self.expense_repo.get_recent_by_user(user_id, limit)

    def get_monthly_expenses(self, user_id: int, month: int, year: int):
        return self.expense_repo.get_by_user_and_month(user_id, month, year)

    def get_monthly_total(self, user_id: int, month: int, year: int) -> float:
        return self.expense_repo.get_total_by_user_and_month(user_id, month, year)

    def get_category_total(self, user_id: int, category_id: int, month: int, year: int) -> float:
        return self.expense_repo.get_total_by_user_category_and_month(user_id, category_id, month, year)

    def create_expense(self, user_id: int, description: str, amount: float, date: date, category_id: int, notes: Optional[str] = None):
        expense_data = ExpenseBase(
            description=description,
            amount=amount,
            date=date,
            category_id=category_id,
            notes=notes,
            user_id=user_id
        )
        return self.expense_repo.create(expense_data)

    def update_expense(self, expense_id: int, description: str, amount: float, date: date, category_id: int, notes: Optional[str]):
        return self.expense_repo.update(expense_id, description, amount, date, category_id, notes)

    def delete_expense(self, expense_id: int):
        return self.expense_repo.delete(expense_id)
