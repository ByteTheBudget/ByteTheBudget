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
    from app.utilities.security import encrypt_password
    from sqlmodel import select

    create_db_and_tables()

    with get_cli_session() as session:
        # seed admin accounts
        admin_accounts = [
            {"username": "bob", "password": "bobpass", "email": "bob@bytethebyte.com"},
            # for the dev team if they want to add another admin account
            # {"username": "yourname", "password": "yourpass", "email": "you@email.com"},
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
                    role="admin"
                ))

        # seed default categories
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

        # seed default subscription templates
        default_templates = [
            {"name": "Netflix", "default_amount": 65.00, "billing_cycle": "monthly"},
            {"name": "Spotify", "default_amount": 20.00, "billing_cycle": "monthly"},
            {"name": "Flow WiFi", "default_amount": 200.00, "billing_cycle": "monthly"},
            {"name": "TSTT", "default_amount": 150.00, "billing_cycle": "monthly"},
            {"name": "Adobe CC", "default_amount": 80.00, "billing_cycle": "monthly"},
            {"name": "YouTube Premium", "default_amount": 30.00, "billing_cycle": "monthly"},
        ]
        for t in default_templates:
            existing = session.exec(
                select(SubscriptionTemplate).where(SubscriptionTemplate.name == t["name"])
            ).first()
            if not existing:
                session.add(SubscriptionTemplate(**t))

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