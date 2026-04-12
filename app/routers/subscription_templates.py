from fastapi import Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.dependencies import SessionDep
from app.dependencies.auth import AdminDep
from app.repositories.subscription_template import SubscriptionTemplateRepository
from app.services.subscription_template_service import SubscriptionTemplateService
from app.utilities.flash import flash
from . import router, templates


@router.get("/admin/subscription-templates", response_class=HTMLResponse)
async def subscription_templates_view(request: Request, user: AdminDep, db: SessionDep):
    template_service = SubscriptionTemplateService(SubscriptionTemplateRepository(db))
    templates_list = template_service.get_all_templates()
    return templates.TemplateResponse(
        request=request,
        name="admin_subscription_templates.html",
        context={"user": user, "templates_list": templates_list}
    )


@router.post("/admin/subscription-templates", response_class=HTMLResponse)
async def add_template_action(
    request: Request,
    user: AdminDep,
    db: SessionDep,
    name: str = Form(),
    default_amount: float = Form(),
    billing_cycle: str = Form()
):
    template_service = SubscriptionTemplateService(SubscriptionTemplateRepository(db))
    try:
        template_service.create_template(name, default_amount, billing_cycle)
        flash(request, "Template created!")
    except Exception as e:
        flash(request, f"Error creating template: {e}", "danger")
    return RedirectResponse(url=request.url_for("subscription_templates_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/admin/subscription-templates/{template_id}/edit", response_class=HTMLResponse)
async def edit_template_action(
    request: Request,
    user: AdminDep,
    db: SessionDep,
    template_id: int,
    name: str = Form(),
    default_amount: float = Form(),
    billing_cycle: str = Form()
):
    template_service = SubscriptionTemplateService(SubscriptionTemplateRepository(db))
    try:
        template_service.update_template(template_id, name, default_amount, billing_cycle)
        flash(request, "Template updated!")
    except Exception as e:
        flash(request, f"Error updating template: {e}", "danger")
    return RedirectResponse(url=request.url_for("subscription_templates_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/admin/subscription-templates/{template_id}/delete", response_class=HTMLResponse)
async def delete_template_action(
    request: Request,
    user: AdminDep,
    db: SessionDep,
    template_id: int
):
    template_service = SubscriptionTemplateService(SubscriptionTemplateRepository(db))
    try:
        template_service.delete_template(template_id)
        flash(request, "Template deleted!")
    except Exception as e:
        flash(request, f"Error deleting template: {e}", "danger")
    return RedirectResponse(url=request.url_for("subscription_templates_view"), status_code=status.HTTP_303_SEE_OTHER)
