from sqlmodel import Session, select
from app.models.category import Category, CategoryBase
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, category_data: CategoryBase) -> Category:
        try:
            category = Category.model_validate(category_data)
            self.db.add(category)
            self.db.commit()
            self.db.refresh(category)
            return category
        except Exception as e:
            logger.error(f"Error creating category: {e}")
            self.db.rollback()
            raise

    def get_all(self) -> list[Category]:
        return self.db.exec(select(Category)).all()

    def get_by_id(self, category_id: int) -> Optional[Category]:
        return self.db.get(Category, category_id)

    def get_by_name(self, name: str) -> Optional[Category]:
        return self.db.exec(select(Category).where(Category.name == name)).one_or_none()

    def update(self, category_id: int, name: str, is_default: bool) -> Category:
        category = self.db.get(Category, category_id)
        if not category:
            raise Exception("Category not found")
        try:
            category.name = name
            category.is_default = is_default
            self.db.add(category)
            self.db.commit()
            self.db.refresh(category)
            return category
        except Exception as e:
            logger.error(f"Error updating category: {e}")
            self.db.rollback()
            raise

    def delete(self, category_id: int):
        category = self.db.get(Category, category_id)
        if not category:
            raise Exception("Category not found")
        try:
            self.db.delete(category)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error deleting category: {e}")
            self.db.rollback()
            raise