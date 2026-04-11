from sqlmodel import Session, select, func
from app.models.income import Income, IncomeBase
from typing import Optional
from datetime import date
import logging

logger = logging.getLogger(__name__)

class IncomeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, income_data: IncomeBase) -> Income:
        try:
            income = Income.model_validate(income_data)
            self.db.add(income)
            self.db.commit()
            self.db.refresh(income)
            return income
        except Exception as e:
            logger.error(f"Error creating income: {e}")
            self.db.rollback()
            raise

    def get_all_by_user(self, user_id: int) -> list[Income]:
        return self.db.exec(select(Income).where(Income.user_id == user_id)).all()

    def get_by_id(self, income_id: int) -> Optional[Income]:
        return self.db.get(Income, income_id)

    def get_total_by_user_and_month(self, user_id: int, month: int, year: int) -> float:
        result = self.db.exec(
            select(func.sum(Income.amount)).where(
                Income.user_id == user_id,
                func.extract("month", Income.date_received) == month,
                func.extract("year", Income.date_received) == year
            )
        ).one_or_none()
        return result or 0.0

    def update(self, income_id: int, source: str, amount: float, type: str, date_received: date) -> Income:
        income = self.db.get(Income, income_id)
        if not income:
            raise Exception("Income not found")
        try:
            income.source = source
            income.amount = amount
            income.type = type
            income.date_received = date_received
            self.db.add(income)
            self.db.commit()
            self.db.refresh(income)
            return income
        except Exception as e:
            logger.error(f"Error updating income: {e}")
            self.db.rollback()
            raise

    def delete(self, income_id: int):
        income = self.db.get(Income, income_id)
        if not income:
            raise Exception("Income not found")
        try:
            self.db.delete(income)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error deleting income: {e}")
            self.db.rollback()
            raise