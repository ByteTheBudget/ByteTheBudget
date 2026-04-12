from app.repositories.budget import BudgetRepository
from app.repositories.expense import ExpenseRepository
from app.models.budget import BudgetBase
from datetime import date

class BudgetService:
    def __init__(self, budget_repo: BudgetRepository, expense_repo: ExpenseRepository):
        self.budget_repo = budget_repo
        self.expense_repo = expense_repo

    def get_all_budgets(self, user_id: int):
        return self.budget_repo.get_all_by_user(user_id)

    def get_budget_by_id(self, budget_id: int):
        return self.budget_repo.get_by_id(budget_id)

    def create_budget(self, user_id: int, category_id: int, limit: float):
        existing = self.budget_repo.get_by_user_and_category(user_id, category_id)
        if existing:
            raise Exception("Budget already exists for this category")
        budget_data = BudgetBase(
            limit=limit,
            user_id=user_id,
            category_id=category_id
        )
        return self.budget_repo.create(budget_data)

    def update_budget(self, budget_id: int, limit: float):
        return self.budget_repo.update(budget_id, limit)

    def delete_budget(self, budget_id: int):
        return self.budget_repo.delete(budget_id)

    def get_budget_progress(self, user_id: int, month: int, year: int):
        budgets = self.budget_repo.get_all_by_user(user_id)
        progress = []
        for budget in budgets:
            spent = self.expense_repo.get_total_by_user_category_and_month(
                user_id, budget.category_id, month, year
            )
            pct = (spent / budget.limit * 100) if budget.limit > 0 else 0
            progress.append({
                "budget": budget,
                "spent": spent,
                "remaining": max(0, budget.limit - spent),
                "percentage": round(pct, 1),
                "is_over": spent > budget.limit,
                "is_warning": pct >= 80
            })
        return progress
