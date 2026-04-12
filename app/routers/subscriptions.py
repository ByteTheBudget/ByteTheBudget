from fastapi import Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import date
from app.dependencies import SessionDep
from app.dependencies.auth import AuthDep
from app.repositories.subscription import SubscriptionRepository
from app.repositories.subscription_template import SubscriptionTemplateRepository
from app.services.subscription_service import SubscriptionService
from app.services.subscription_template_service import SubscriptionTemplateService
from app.utilities.flash import flash
from . import router, templates


@router.get("/app/subscriptions", response_class=HTMLResponse)
async def subscriptions_view(request: Request, user: AuthDep, db: SessionDep):
    sub_service = SubscriptionService(SubscriptionRepository(db), SubscriptionTemplateRepository(db))
    template_service = SubscriptionTemplateService(SubscriptionTemplateRepository(db))
    subscriptions = sub_service.get_all_subscriptions(user.id)
    templates_list = template_service.get_all_templates()
    monthly_total = sub_service.get_monthly_total(user.id)
    upcoming = sub_service.get_upcoming_renewals(user.id)
    return templates.TemplateResponse(
        request=request,
        name="subscriptions.html",
        context={
            "user": user,
            "subscriptions": subscriptions,
            "templates_list": templates_list,
            "monthly_total": monthly_total,
            "upcoming": upcoming
        }
    )


@router.post("/app/subscriptions", response_class=HTMLResponse)
async def add_subscription_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    name: str = Form(),
    amount: float = Form(),
    billing_cycle: str = Form(),
    next_renewal: date = Form()
):
    sub_service = SubscriptionService(SubscriptionRepository(db))
    try:
        sub_service.create_subscription(user.id, name, amount, billing_cycle, next_renewal)
        flash(request, "Subscription added!")
    except Exception as e:
        flash(request, f"Error adding subscription: {e}", "danger")
    return RedirectResponse(url=request.url_for("subscriptions_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/app/subscriptions/from-template", response_class=HTMLResponse)
async def add_subscription_from_template_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    template_id: int = Form(),
    next_renewal: date = Form()
):
    sub_service = SubscriptionService(SubscriptionRepository(db), SubscriptionTemplateRepository(db))
    try:
        sub_service.create_from_template(user.id, template_id, next_renewal)
        flash(request, "Subscription added from template!")
    except Exception as e:
        flash(request, f"Error adding subscription: {e}", "danger")
    return RedirectResponse(url=request.url_for("subscriptions_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/app/subscriptions/{subscription_id}/edit", response_class=HTMLResponse)
async def edit_subscription_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    subscription_id: int,
    name: str = Form(),
    amount: float = Form(),
    billing_cycle: str = Form(),
    next_renewal: date = Form(),
    is_active: bool = Form(default=False)
):
    sub_service = SubscriptionService(SubscriptionRepository(db))
    sub = sub_service.get_subscription_by_id(subscription_id)
    if not sub or sub.user_id != user.id:
        flash(request, "Subscription not found", "danger")
        return RedirectResponse(url=request.url_for("subscriptions_view"), status_code=status.HTTP_303_SEE_OTHER)
    try:
        sub_service.update_subscription(subscription_id, name, amount, billing_cycle, next_renewal, is_active)
        flash(request, "Subscription updated!")
    except Exception as e:
        flash(request, f"Error updating subscription: {e}", "danger")
    return RedirectResponse(url=request.url_for("subscriptions_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/app/subscriptions/{subscription_id}/delete", response_class=HTMLResponse)
async def delete_subscription_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    subscription_id: int
):
    sub_service = SubscriptionService(SubscriptionRepository(db))
    sub = sub_service.get_subscription_by_id(subscription_id)
    if not sub or sub.user_id != user.id:
        flash(request, "Subscription not found", "danger")
        return RedirectResponse(url=request.url_for("subscriptions_view"), status_code=status.HTTP_303_SEE_OTHER)
    try:
        sub_service.delete_subscription(subscription_id)
        flash(request, "Subscription deleted!")
    except Exception as e:
        flash(request, f"Error deleting subscription: {e}", "danger")
    return RedirectResponse(url=request.url_for("subscriptions_view"), status_code=status.HTTP_303_SEE_OTHER)