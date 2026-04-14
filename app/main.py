import uvicorn
from fastapi import FastAPI, Request, status
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from app.routers import templates, static_files, router, api_router
from app.config import get_settings
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.database import create_db_and_tables, get_cli_session
    from app.models.user import User
    from app.models.category import Category
    from app.models.subscription_template import SubscriptionTemplate
    from app.models.expense import Expense
    from app.models.income import Income
    from app.models.budget import Budget
    from app.models.subscription import Subscription
    from app.utilities.security import encrypt_password
    from sqlmodel import select
    from datetime import date

    create_db_and_tables()

    with get_cli_session() as session:
        # ── ACCOUNTS ─────────────────────────────────────────────────────────
        admin_accounts = [
            {"username": "bob",   "password": "bobpass",   "email": "bob@bytethebyte.com",   "role": "admin"},
            {"username": "alice", "password": "alicepass", "email": "alice@bytethebyte.com", "role": "user"},
        ]
        for account in admin_accounts:
            existing = session.exec(
                select(User).where(User.username == account["username"])
            ).first()
            if not existing:
                session.add(User(
                    username=account["username"],
                    email=account["email"],
                    password=encrypt_password(account["password"]),
                    role=account["role"]
                ))

        # ── DEFAULT CATEGORIES ───────────────────────────────────────────────
        default_categories = [
            "Food", "Transport", "Entertainment", "Rent",
            "Education", "Health", "Utilities", "Clothing",
            "Savings", "Other"
        ]
        for name in default_categories:
            existing = session.exec(
                select(Category).where(Category.name == name)
            ).first()
            if not existing:
                session.add(Category(name=name, is_default=True))

        # ── DEFAULT SUBSCRIPTION TEMPLATES ───────────────────────────────────
        default_templates = [
            {"name": "Netflix",          "default_amount": 65.00,  "billing_cycle": "monthly"},
            {"name": "Spotify",          "default_amount": 20.00,  "billing_cycle": "monthly"},
            {"name": "Flow WiFi",        "default_amount": 200.00, "billing_cycle": "monthly"},
            {"name": "TSTT",             "default_amount": 150.00, "billing_cycle": "monthly"},
            {"name": "Adobe CC",         "default_amount": 80.00,  "billing_cycle": "monthly"},
            {"name": "YouTube Premium",  "default_amount": 30.00,  "billing_cycle": "monthly"},
        ]
        for t in default_templates:
            existing = session.exec(
                select(SubscriptionTemplate).where(SubscriptionTemplate.name == t["name"])
            ).first()
            if not existing:
                session.add(SubscriptionTemplate(**t))

        session.commit()

        # ── BOB'S SEED DATA ──────────────────────────────────────────────────
        bob = session.exec(select(User).where(User.username == "bob")).first()

        def cat_id(name):
            return session.exec(select(Category).where(Category.name == name)).first().id

        # INCOME — April 2026
        bob_income = [
            {"source": "Monthly Allowance", "amount": 3800.00, "type": "Allowance",  "date_received": date(2026, 4, 1)},
            {"source": "Part-Time Job",      "amount": 2400.00, "type": "Employment", "date_received": date(2026, 4, 1)},
        ]
        for i in bob_income:
            existing = session.exec(
                select(Income).where(
                    Income.user_id == bob.id,
                    Income.source == i["source"],
                    Income.date_received == i["date_received"]
                )
            ).first()
            if not existing:
                session.add(Income(**i, user_id=bob.id))

        # EXPENSES — April 2026
        bob_expenses = [
            # April
            {"description": "Subway Sandwich", "amount": 45.00,   "date": date(2026, 4, 10), "category": "Food",          "notes": None},
            {"description": "Maxi Taxi",        "amount": 8.00,    "date": date(2026, 4, 11), "category": "Transport",     "notes": None},
            {"description": "Movie Tickets",    "amount": 160.00,  "date": date(2026, 4, 8),  "category": "Entertainment", "notes": "Cinema with friends"},
            {"description": "Textbooks",        "amount": 340.00,  "date": date(2026, 4, 5),  "category": "Education",     "notes": None},
            {"description": "Groceries",        "amount": 220.00,  "date": date(2026, 4, 3),  "category": "Food",          "notes": None},
            {"description": "Rent",             "amount": 2500.00, "date": date(2026, 4, 1),  "category": "Rent",          "notes": "April rent"},

        ]
        for e in bob_expenses:
            existing = session.exec(
                select(Expense).where(
                    Expense.user_id == bob.id,
                    Expense.description == e["description"],
                    Expense.date == e["date"]
                )
            ).first()
            if not existing:
                session.add(Expense(
                    description=e["description"],
                    amount=e["amount"],
                    date=e["date"],
                    notes=e["notes"],
                    user_id=bob.id,
                    category_id=cat_id(e["category"])
                ))

        # BUDGETS
        bob_budgets = [
            {"category": "Food",          "limit": 800.00},
            {"category": "Transport",     "limit": 300.00},
            {"category": "Entertainment", "limit": 400.00},
            {"category": "Rent",          "limit": 2500.00},
            {"category": "Education",     "limit": 500.00},
            {"category": "Health",        "limit": 200.00},
            {"category": "Clothing",      "limit": 400.00},
            {"category": "Utilities",     "limit": 300.00},
        ]
        for b in bob_budgets:
            existing = session.exec(
                select(Budget).where(
                    Budget.user_id == bob.id,
                    Budget.category_id == cat_id(b["category"])
                )
            ).first()
            if not existing:
                session.add(Budget(
                    limit=b["limit"],
                    user_id=bob.id,
                    category_id=cat_id(b["category"])
                ))

        # SUBSCRIPTIONS
        bob_subscriptions = [
            {"name": "Netflix",         "amount": 65.00,  "billing_cycle": "monthly", "next_renewal": date(2026, 5, 1)},
            {"name": "Spotify",         "amount": 20.00,  "billing_cycle": "monthly", "next_renewal": date(2026, 5, 1)},
            {"name": "Flow WiFi",       "amount": 200.00, "billing_cycle": "monthly", "next_renewal": date(2026, 5, 2)},
            {"name": "Adobe CC",        "amount": 80.00,  "billing_cycle": "monthly", "next_renewal": date(2026, 5, 10)},
            {"name": "YouTube Premium", "amount": 30.00,  "billing_cycle": "monthly", "next_renewal": date(2026, 5, 15)},
        ]
        for s in bob_subscriptions:
            existing = session.exec(
                select(Subscription).where(
                    Subscription.user_id == bob.id,
                    Subscription.name == s["name"]
                )
            ).first()
            if not existing:
                session.add(Subscription(**s, user_id=bob.id))

        session.commit()

    yield


app = FastAPI(
    middleware=[
        Middleware(SessionMiddleware, secret_key=get_settings().secret_key)
    ],
    lifespan=lifespan
)

app.include_router(router)
app.include_router(api_router)
app.mount("/static", static_files, name="static")


@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def unauthorized_redirect_handler(request: Request, exc: Exception):
    return templates.TemplateResponse(
        request=request,
        name="401.html",
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=get_settings().app_host,
        port=get_settings().app_port,
        reload=get_settings().env.lower() != "production"
    )