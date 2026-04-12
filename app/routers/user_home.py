from fastapi import Request
from fastapi.responses import HTMLResponse
from datetime import datetime
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.repositories.expense import ExpenseRepository
from app.repositories.income import IncomeRepository
from app.repositories.subscription import SubscriptionRepository
from app.repositories.budget import BudgetRepository
from app.services.expense_service import ExpenseService
from app.services.income_service import IncomeService
from app.services.subscription_service import SubscriptionService
from app.services.budget_service import BudgetService
from . import router, templates


@router.get("/app", response_class=HTMLResponse)
async def user_home_view(request: Request, user: AuthDep, db: SessionDep):
    now = datetime.now()
    month, year = now.month, now.year

    expense_service = ExpenseService(ExpenseRepository(db))
    income_service = IncomeService(IncomeRepository(db))
    sub_service = SubscriptionService(SubscriptionRepository(db))
    budget_service = BudgetService(BudgetRepository(db), ExpenseRepository(db))

    total_income = income_service.get_monthly_total(user.id, month, year)
    total_expenses = expense_service.get_monthly_total(user.id, month, year)
    total_subscriptions = sub_service.get_monthly_total(user.id)
    budget_progress = budget_service.get_budget_progress(user.id, month, year)
    recent_expenses = expense_service.get_recent_expenses(user.id, 5)
    alerts = [b for b in budget_progress if b["is_warning"]]

    monthly_expenses = expense_service.get_monthly_expenses(user.id, month, year)
    burn_rate_data = {}
    for expense in monthly_expenses:
        day = expense.date.day
        burn_rate_data[day] = burn_rate_data.get(day, 0) + expense.amount
    burn_rate = [{"day": d, "amount": a} for d, a in sorted(burn_rate_data.items())]

    return templates.TemplateResponse(
        request=request,
        name="app.html",
        context={
            "user": user,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "total_subscriptions": total_subscriptions,
            "remaining": total_income - total_expenses - total_subscriptions,
            "budget_progress": budget_progress,
            "recent_expenses": recent_expenses,
            "alerts": alerts,
            "burn_rate": burn_rate,
            "month": now.strftime("%B %Y")
        }
    )