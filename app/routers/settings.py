from fastapi import Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.dependencies import SessionDep
from app.dependencies.auth import AuthDep
from app.repositories.user import UserRepository
from app.services.user_service import UserService
from app.utilities.flash import flash
from app.utilities.security import encrypt_password, verify_password
from . import router, templates


@router.get("/app/settings", response_class=HTMLResponse)
async def settings_view(request: Request, user: AuthDep, db: SessionDep):
    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={"user": user}
    )


@router.post("/app/settings/profile", response_class=HTMLResponse)
async def update_profile_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    username: str = Form(),
    email: str = Form()
):
    user_repo = UserRepository(db)
    try:
        user.username = username
        user.email = email
        db.add(user)
        db.commit()
        flash(request, "Profile updated!")
    except Exception as e:
        flash(request, f"Error updating profile: {e}", "danger")
    return RedirectResponse(url=request.url_for("settings_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/app/settings/password", response_class=HTMLResponse)
async def update_password_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    current_password: str = Form(),
    new_password: str = Form(),
    confirm_password: str = Form()
):
    if new_password != confirm_password:
        flash(request, "New passwords do not match", "danger")
        return RedirectResponse(url=request.url_for("settings_view"), status_code=status.HTTP_303_SEE_OTHER)
    if not verify_password(current_password, user.password):
        flash(request, "Current password is incorrect", "danger")
        return RedirectResponse(url=request.url_for("settings_view"), status_code=status.HTTP_303_SEE_OTHER)
    try:
        user.password = encrypt_password(new_password)
        db.add(user)
        db.commit()
        flash(request, "Password updated!")
    except Exception as e:
        flash(request, f"Error updating password: {e}", "danger")
    return RedirectResponse(url=request.url_for("settings_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/app/settings/delete-account", response_class=HTMLResponse)
async def delete_account_action(
    request: Request,
    user: AuthDep,
    db: SessionDep
):
    try:
        db.delete(user)
        db.commit()
        response = RedirectResponse(url=request.url_for("login_view"), status_code=status.HTTP_303_SEE_OTHER)
        response.delete_cookie(key="access_token", httponly=True, samesite="none", secure=True)
        return response
    except Exception as e:
        flash(request, f"Error deleting account: {e}", "danger")
        return RedirectResponse(url=request.url_for("settings_view"), status_code=status.HTTP_303_SEE_OTHER)
