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
    from sqlmodel import select
    from pwdlib import PasswordHash

    create_db_and_tables()

    pwd_context = PasswordHash.recommended()

    admin_accounts = [
        {"username": "bob", "password": "bobpass", "email": "bob@bytethebyte.com"},
        # add your dev team accounts here:
        # {"username": "yourname", "password": "yourpass", "email": "you@email.com"},
    ]

    with get_cli_session() as session:
        for account in admin_accounts:
            existing = session.exec(
                select(User).where(User.username == account["username"])
            ).first()
            if not existing:
                user = User(
                    username=account["username"],
                    email=account["email"],
                    password=pwd_context.hash(account["password"]),
                    role="admin"
                )
                session.add(user)
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