from fastapi import Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.dependencies import SessionDep
from app.dependencies.auth import AdminDep
from app.repositories.user import UserRepository
from app.services.user_service import UserService
from app.utilities.flash import flash
from . import router, templates


@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users_view(request: Request, user: AdminDep, db: SessionDep):
    user_service = UserService(UserRepository(db))
    all_users = user_service.get_all_users()
    return templates.TemplateResponse(
        request=request,
        name="admin_users.html",
        context={"user": user, "all_users": all_users}
    )


@router.post("/admin/users/{target_user_id}/deactivate", response_class=HTMLResponse)
async def deactivate_user_action(
    request: Request,
    user: AdminDep,
    db: SessionDep,
    target_user_id: int
):
    user_repo = UserRepository(db)
    target = user_repo.get_by_id(target_user_id)
    if not target:
        flash(request, "User not found", "danger")
        return RedirectResponse(url=request.url_for("admin_users_view"), status_code=status.HTTP_303_SEE_OTHER)
    try:
        target.is_active = False
        db.add(target)
        db.commit()
        flash(request, f"User {target.username} deactivated")
    except Exception as e:
        flash(request, f"Error: {e}", "danger")
    return RedirectResponse(url=request.url_for("admin_users_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/admin/users/{target_user_id}/reactivate", response_class=HTMLResponse)
async def reactivate_user_action(
    request: Request,
    user: AdminDep,
    db: SessionDep,
    target_user_id: int
):
    user_repo = UserRepository(db)
    target = user_repo.get_by_id(target_user_id)
    if not target:
        flash(request, "User not found", "danger")
        return RedirectResponse(url=request.url_for("admin_users_view"), status_code=status.HTTP_303_SEE_OTHER)
    try:
        target.is_active = True
        db.add(target)
        db.commit()
        flash(request, f"User {target.username} reactivated")
    except Exception as e:
        flash(request, f"Error: {e}", "danger")
    return RedirectResponse(url=request.url_for("admin_users_view"), status_code=status.HTTP_303_SEE_OTHER)
