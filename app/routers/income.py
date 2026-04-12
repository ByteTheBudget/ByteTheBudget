from fastapi import Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import date
from app.dependencies import SessionDep
from app.dependencies.auth import AuthDep
from app.repositories.income import IncomeRepository
from app.services.income_service import IncomeService
from app.utilities.flash import flash
from . import router, templates


@router.get("/app/income", response_class=HTMLResponse)
async def income_view(request: Request, user: AuthDep, db: SessionDep):
    income_service = IncomeService(IncomeRepository(db))
    income_list = income_service.get_all_income(user.id)
    from datetime import datetime
    now = datetime.now()
    monthly_total = income_service.get_monthly_total(user.id, now.month, now.year)
    return templates.TemplateResponse(
        request=request,
        name="income.html",
        context={"user": user, "income_list": income_list, "monthly_total": monthly_total}
    )


@router.post("/app/income", response_class=HTMLResponse)
async def add_income_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    source: str = Form(),
    amount: float = Form(),
    type: str = Form(),
    date_received: date = Form()
):
    income_service = IncomeService(IncomeRepository(db))
    try:
        income_service.create_income(user.id, source, amount, type, date_received)
        flash(request, "Income added successfully!")
    except Exception as e:
        flash(request, f"Error adding income: {e}", "danger")
    return RedirectResponse(url=request.url_for("income_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/app/income/{income_id}/edit", response_class=HTMLResponse)
async def edit_income_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    income_id: int,
    source: str = Form(),
    amount: float = Form(),
    type: str = Form(),
    date_received: date = Form()
):
    income_service = IncomeService(IncomeRepository(db))
    income = income_service.get_income_by_id(income_id)
    if not income or income.user_id != user.id:
        flash(request, "Income record not found", "danger")
        return RedirectResponse(url=request.url_for("income_view"), status_code=status.HTTP_303_SEE_OTHER)
    try:
        income_service.update_income(income_id, source, amount, type, date_received)
        flash(request, "Income updated!")
    except Exception as e:
        flash(request, f"Error updating income: {e}", "danger")
    return RedirectResponse(url=request.url_for("income_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/app/income/{income_id}/delete", response_class=HTMLResponse)
async def delete_income_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    income_id: int
):
    income_service = IncomeService(IncomeRepository(db))
    income = income_service.get_income_by_id(income_id)
    if not income or income.user_id != user.id:
        flash(request, "Income record not found", "danger")
        return RedirectResponse(url=request.url_for("income_view"), status_code=status.HTTP_303_SEE_OTHER)
    try:
        income_service.delete_income(income_id)
        flash(request, "Income deleted!")
    except Exception as e:
        flash(request, f"Error deleting income: {e}", "danger")
    return RedirectResponse(url=request.url_for("income_view"), status_code=status.HTTP_303_SEE_OTHER)