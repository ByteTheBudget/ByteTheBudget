from fastapi import Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime
from app.dependencies import SessionDep
from app.dependencies.auth import AuthDep
from app.repositories.budget import BudgetRepository
from app.repositories.expense import ExpenseRepository
from app.repositories.category import CategoryRepository
from app.services.budget_service import BudgetService
from app.services.category_service import CategoryService
from app.utilities.flash import flash
from . import router, templates


@router.get("/app/budgets", response_class=HTMLResponse)
async def budgets_view(request: Request, user: AuthDep, db: SessionDep):
    budget_service = BudgetService(BudgetRepository(db), ExpenseRepository(db))
    category_service = CategoryService(CategoryRepository(db))
    now = datetime.now()
    budget_progress = budget_service.get_budget_progress(user.id, now.month, now.year)
    categories = category_service.get_all_categories()
    return templates.TemplateResponse(
        request=request,
        name="budgets.html",
        context={
            "user": user,
            "budget_progress": budget_progress,
            "categories": categories
        }
    )


@router.post("/app/budgets", response_class=HTMLResponse)
async def add_budget_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    category_id: int = Form(),
    limit: float = Form()
):
    budget_service = BudgetService(BudgetRepository(db), ExpenseRepository(db))
    try:
        budget_service.create_budget(user.id, category_id, limit)
        flash(request, "Budget created!")
    except Exception as e:
        flash(request, f"Error creating budget: {e}", "danger")
    return RedirectResponse(url=request.url_for("budgets_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/app/budgets/{budget_id}/edit", response_class=HTMLResponse)
async def edit_budget_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    budget_id: int,
    limit: float = Form()
):
    budget_service = BudgetService(BudgetRepository(db), ExpenseRepository(db))
    budget = budget_service.get_budget_by_id(budget_id)
    if not budget or budget.user_id != user.id:
        flash(request, "Budget not found", "danger")
        return RedirectResponse(url=request.url_for("budgets_view"), status_code=status.HTTP_303_SEE_OTHER)
    try:
        budget_service.update_budget(budget_id, limit)
        flash(request, "Budget updated!")
    except Exception as e:
        flash(request, f"Error updating budget: {e}", "danger")
    return RedirectResponse(url=request.url_for("budgets_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/app/budgets/{budget_id}/delete", response_class=HTMLResponse)
async def delete_budget_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    budget_id: int
):
    budget_service = BudgetService(BudgetRepository(db), ExpenseRepository(db))
    budget = budget_service.get_budget_by_id(budget_id)
    if not budget or budget.user_id != user.id:
        flash(request, "Budget not found", "danger")
        return RedirectResponse(url=request.url_for("budgets_view"), status_code=status.HTTP_303_SEE_OTHER)
    try:
        budget_service.delete_budget(budget_id)
        flash(request, "Budget deleted!")
    except Exception as e:
        flash(request, f"Error deleting budget: {e}", "danger")
    return RedirectResponse(url=request.url_for("budgets_view"), status_code=status.HTTP_303_SEE_OTHER)
