from fastapi import Request, status
from fastapi.responses import HTMLResponse
from datetime import datetime
from app.dependencies import SessionDep
from app.dependencies.auth import AuthDep
from app.repositories.expense import ExpenseRepository
from app.repositories.income import IncomeRepository
from app.repositories.subscription import SubscriptionRepository
from app.repositories.budget import BudgetRepository
from app.repositories.category import CategoryRepository
from app.services.expense_service import ExpenseService
from app.services.income_service import IncomeService
from app.services.subscription_service import SubscriptionService
from app.services.budget_service import BudgetService
from app.services.category_service import CategoryService
from . import router, templates


@router.get("/app/reports", response_class=HTMLResponse)
async def reports_view(request: Request, user: AuthDep, db: SessionDep):
    now = datetime.now()
    month = now.month
    year = now.year

    expense_service = ExpenseService(ExpenseRepository(db))
    income_service = IncomeService(IncomeRepository(db))
    sub_service = SubscriptionService(SubscriptionRepository(db))
    budget_service = BudgetService(BudgetRepository(db), ExpenseRepository(db))
    category_service = CategoryService(CategoryRepository(db))

    # data for charts
    monthly_expenses = expense_service.get_monthly_expenses(user.id, month, year)
    total_expenses = expense_service.get_monthly_total(user.id, month, year)
    total_income = income_service.get_monthly_total(user.id, month, year)
    total_subscriptions = sub_service.get_monthly_total(user.id)
    budget_progress = budget_service.get_budget_progress(user.id, month, year)
    categories = category_service.get_all_categories()
    upcoming_renewals = sub_service.get_upcoming_renewals(user.id)

    # spending by category for pie chart
    spending_by_category = []
    for cat in categories:
        spent = expense_service.get_category_total(user.id, cat.id, month, year)
        if spent > 0:
            spending_by_category.append({"category": cat.name, "amount": spent})

    # burn rate — daily spending this month grouped by day
    burn_rate_data = {}
    for expense in monthly_expenses:
        day = expense.date.day
        burn_rate_data[day] = burn_rate_data.get(day, 0) + expense.amount
    burn_rate = [{"day": d, "amount": a} for d, a in sorted(burn_rate_data.items())]

    return templates.TemplateResponse(
        request=request,
        name="reports.html",
        context={
            "user": user,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "total_subscriptions": total_subscriptions,
            "remaining": total_income - total_expenses - total_subscriptions,
            "budget_progress": budget_progress,
            "spending_by_category": spending_by_category,
            "burn_rate": burn_rate,
            "upcoming_renewals": upcoming_renewals,
            "month": now.strftime("%B %Y")
        }
    )
