from sqlmodel import Session, select
from app.models.budget import Budget, BudgetBase
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class BudgetRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, budget_data: BudgetBase) -> Budget:
        try:
            budget = Budget.model_validate(budget_data)
            self.db.add(budget)
            self.db.commit()
            self.db.refresh(budget)
            return budget
        except Exception as e:
            logger.error(f"Error creating budget: {e}")
            self.db.rollback()
            raise

    def get_all_by_user(self, user_id: int) -> list[Budget]:
        return self.db.exec(select(Budget).where(Budget.user_id == user_id)).all()

    def get_by_id(self, budget_id: int) -> Optional[Budget]:
        return self.db.get(Budget, budget_id)

    def get_by_user_and_category(self, user_id: int, category_id: int) -> Optional[Budget]:
        return self.db.exec(
            select(Budget).where(
                Budget.user_id == user_id,
                Budget.category_id == category_id
            )
        ).one_or_none()

    def update(self, budget_id: int, limit: float) -> Budget:
        budget = self.db.get(Budget, budget_id)
        if not budget:
            raise Exception("Budget not found")
        try:
            budget.limit = limit
            self.db.add(budget)
            self.db.commit()
            self.db.refresh(budget)
            return budget
        except Exception as e:
            logger.error(f"Error updating budget: {e}")
            self.db.rollback()
            raise

    def delete(self, budget_id: int):
        budget = self.db.get(Budget, budget_id)
        if not budget:
            raise Exception("Budget not found")
        try:
            self.db.delete(budget)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error deleting budget: {e}")
            self.db.rollback()
            raise