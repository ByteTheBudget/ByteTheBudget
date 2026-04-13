from fastapi import Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional
from datetime import date
from app.dependencies import SessionDep
from app.dependencies.auth import AuthDep
from app.repositories.expense import ExpenseRepository
from app.repositories.category import CategoryRepository
from app.services.expense_service import ExpenseService
from app.services.category_service import CategoryService
from app.utilities.flash import flash
from . import router, templates


@router.get("/app/expenses", response_class=HTMLResponse)
async def expenses_view(request: Request, user: AuthDep, db: SessionDep):
    expense_service = ExpenseService(ExpenseRepository(db))
    category_service = CategoryService(CategoryRepository(db))
    expenses = expense_service.get_all_expenses(user.id)
    categories = category_service.get_all_categories()
    categories = category_service.get_all_categories()
    category_map = {cat.id: cat.name for cat in categories}
    return templates.TemplateResponse(
        request=request,
        name="expenses.html",
        context={"user": user, "expenses": expenses, "categories": categories, "category_map": category_map,}
    )


@router.post("/app/expenses", response_class=HTMLResponse)
async def add_expense_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    description: str = Form(),
    amount: float = Form(),
    date: date = Form(),
    category_id: int = Form(),
    notes: Optional[str] = Form(default=None)
):
    expense_service = ExpenseService(ExpenseRepository(db))
    try:
        expense_service.create_expense(user.id, description, amount, date, category_id, notes)
        flash(request, "Expense added successfully!")
    except Exception as e:
        flash(request, f"Error adding expense: {e}", "danger")
    return RedirectResponse(url=request.url_for("expenses_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/app/expenses/{expense_id}/edit", response_class=HTMLResponse)
async def edit_expense_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    expense_id: int,
    description: str = Form(),
    amount: float = Form(),
    date: date = Form(),
    category_id: int = Form(),
    notes: Optional[str] = Form(default=None)
):
    expense_service = ExpenseService(ExpenseRepository(db))
    expense = expense_service.get_expense_by_id(expense_id)
    if not expense or expense.user_id != user.id:
        flash(request, "Expense not found", "danger")
        return RedirectResponse(url=request.url_for("expenses_view"), status_code=status.HTTP_303_SEE_OTHER)
    try:
        expense_service.update_expense(expense_id, description, amount, date, category_id, notes)
        flash(request, "Expense updated!")
    except Exception as e:
        flash(request, f"Error updating expense: {e}", "danger")
    return RedirectResponse(url=request.url_for("expenses_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/app/expenses/{expense_id}/delete", response_class=HTMLResponse)
async def delete_expense_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    expense_id: int
):
    expense_service = ExpenseService(ExpenseRepository(db))
    expense = expense_service.get_expense_by_id(expense_id)
    if not expense or expense.user_id != user.id:
        flash(request, "Expense not found", "danger")
        return RedirectResponse(url=request.url_for("expenses_view"), status_code=status.HTTP_303_SEE_OTHER)
    try:
        expense_service.delete_expense(expense_id)
        flash(request, "Expense deleted!")
    except Exception as e:
        flash(request, f"Error deleting expense: {e}", "danger")
    return RedirectResponse(url=request.url_for("expenses_view"), status_code=status.HTTP_303_SEE_OTHER)