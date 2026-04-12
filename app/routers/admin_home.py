from fastapi import Request
from fastapi.responses import HTMLResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AdminDep
from app.repositories.user import UserRepository
from app.repositories.category import CategoryRepository
from app.repositories.subscription_template import SubscriptionTemplateRepository
from . import router, templates


@router.get("/admin", response_class=HTMLResponse)
async def admin_home_view(request: Request, user: AdminDep, db: SessionDep):
    user_repo = UserRepository(db)
    all_users = user_repo.get_all_users()

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "user": user,
            "total_users": len(all_users),
            "active_users": len([u for u in all_users if u.is_active]),
            "total_categories": len(CategoryRepository(db).get_all()),
            "total_templates": len(SubscriptionTemplateRepository(db).get_all()),
        }
    )