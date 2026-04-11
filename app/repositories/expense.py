from sqlmodel import Session, select, func
from app.models.expense import Expense, ExpenseBase
from typing import Optional
from datetime import date
import logging

logger = logging.getLogger(__name__)

class ExpenseRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, expense_data: ExpenseBase) -> Expense:
        try:
            expense = Expense.model_validate(expense_data)
            self.db.add(expense)
            self.db.commit()
            self.db.refresh(expense)
            return expense
        except Exception as e:
            logger.error(f"Error creating expense: {e}")
            self.db.rollback()
            raise

    def get_all_by_user(self, user_id: int) -> list[Expense]:
        return self.db.exec(select(Expense).where(Expense.user_id == user_id)).all()

    def get_by_id(self, expense_id: int) -> Optional[Expense]:
        return self.db.get(Expense, expense_id)

    def get_by_user_and_month(self, user_id: int, month: int, year: int) -> list[Expense]:
        return self.db.exec(
            select(Expense).where(
                Expense.user_id == user_id,
                func.extract("month", Expense.date) == month,
                func.extract("year", Expense.date) == year
            )
        ).all()

    def get_total_by_user_and_month(self, user_id: int, month: int, year: int) -> float:
        result = self.db.exec(
            select(func.sum(Expense.amount)).where(
                Expense.user_id == user_id,
                func.extract("month", Expense.date) == month,
                func.extract("year", Expense.date) == year
            )
        ).one_or_none()
        return result or 0.0

    def get_total_by_user_category_and_month(self, user_id: int, category_id: int, month: int, year: int) -> float:
        result = self.db.exec(
            select(func.sum(Expense.amount)).where(
                Expense.user_id == user_id,
                Expense.category_id == category_id,
                func.extract("month", Expense.date) == month,
                func.extract("year", Expense.date) == year
            )
        ).one_or_none()
        return result or 0.0

    def get_recent_by_user(self, user_id: int, limit: int = 5) -> list[Expense]:
        return self.db.exec(
            select(Expense).where(Expense.user_id == user_id)
            .order_by(Expense.date.desc())
            .limit(limit)
        ).all()

    def update(self, expense_id: int, description: str, amount: float, date: date, category_id: int, notes: Optional[str]) -> Expense:
        expense = self.db.get(Expense, expense_id)
        if not expense:
            raise Exception("Expense not found")
        try:
            expense.description = description
            expense.amount = amount
            expense.date = date
            expense.category_id = category_id
            expense.notes = notes
            self.db.add(expense)
            self.db.commit()
            self.db.refresh(expense)
            return expense
        except Exception as e:
            logger.error(f"Error updating expense: {e}")
            self.db.rollback()
            raise

    def delete(self, expense_id: int):
        expense = self.db.get(Expense, expense_id)
        if not expense:
            raise Exception("Expense not found")
        try:
            self.db.delete(expense)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error deleting expense: {e}")
            self.db.rollback()
            raise