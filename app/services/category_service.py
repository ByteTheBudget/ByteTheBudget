from app.repositories.category import CategoryRepository

class CategoryService:
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    def get_all_categories(self):
        return self.category_repo.get_all()

    def get_category_by_id(self, category_id: int):
        return self.category_repo.get_by_id(category_id)

    def create_category(self, name: str, is_default: bool = True):
        existing = self.category_repo.get_by_name(name)
        if existing:
            raise Exception("Category already exists")
        from app.models.category import CategoryBase
        category_data = CategoryBase(name=name, is_default=is_default)
        return self.category_repo.create(category_data)

    def update_category(self, category_id: int, name: str, is_default: bool):
        return self.category_repo.update(category_id, name, is_default)

    def delete_category(self, category_id: int):
        return self.category_repo.delete(category_id)
