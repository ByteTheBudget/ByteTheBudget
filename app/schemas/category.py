from sqlmodel import SQLModel


class CategoryCreate(SQLModel):
    name: str
    is_default: bool = True


class CategoryUpdate(SQLModel):
    name: str
    is_default: bool


class CategoryResponse(SQLModel):
    id: int
    name: str
    is_default: bool