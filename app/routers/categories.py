from fastapi import Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.dependencies import SessionDep
from app.dependencies.auth import AdminDep
from app.repositories.category import CategoryRepository
from app.services.category_service import CategoryService
from app.utilities.flash import flash
from . import router, templates


@router.get("/admin/categories", response_class=HTMLResponse)
async def categories_view(request: Request, user: AdminDep, db: SessionDep):
    category_service = CategoryService(CategoryRepository(db))
    categories = category_service.get_all_categories()
    return templates.TemplateResponse(
        request=request,
        name="admin_categories.html",
        context={"user": user, "categories": categories}
    )


@router.post("/admin/categories", response_class=HTMLResponse)
async def add_category_action(
    request: Request,
    user: AdminDep,
    db: SessionDep,
    name: str = Form(),
    is_default: bool = Form(default=True)
):
    category_service = CategoryService(CategoryRepository(db))
    try:
        category_service.create_category(name, is_default)
        flash(request, "Category created!")
    except Exception as e:
        flash(request, f"Error creating category: {e}", "danger")
    return RedirectResponse(url=request.url_for("categories_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/admin/categories/{category_id}/edit", response_class=HTMLResponse)
async def edit_category_action(
    request: Request,
    user: AdminDep,
    db: SessionDep,
    category_id: int,
    name: str = Form(),
    is_default: bool = Form(default=True)
):
    category_service = CategoryService(CategoryRepository(db))
    try:
        category_service.update_category(category_id, name, is_default)
        flash(request, "Category updated!")
    except Exception as e:
        flash(request, f"Error updating category: {e}", "danger")
    return RedirectResponse(url=request.url_for("categories_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/admin/categories/{category_id}/delete", response_class=HTMLResponse)
async def delete_category_action(
    request: Request,
    user: AdminDep,
    db: SessionDep,
    category_id: int
):
    category_service = CategoryService(CategoryRepository(db))
    try:
        category_service.delete_category(category_id)
        flash(request, "Category deleted!")
    except Exception as e:
        flash(request, f"Error deleting category: {e}", "danger")
    return RedirectResponse(url=request.url_for("categories_view"), status_code=status.HTTP_303_SEE_OTHER)
