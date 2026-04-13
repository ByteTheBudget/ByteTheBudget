from fastapi import Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from app.dependencies import SessionDep
from app.dependencies.auth import AuthDep
from app.repositories.expense import ExpenseRepository
from app.repositories.income import IncomeRepository
from app.repositories.subscription import SubscriptionRepository
from app.services.expense_service import ExpenseService
from app.services.income_service import IncomeService
from app.services.subscription_service import SubscriptionService
from app.config import get_settings
from datetime import datetime
import httpx
from . import router, templates

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

@router.get("/app/ai-chat", response_class=HTMLResponse)
async def ai_chat_view(request: Request, user: AuthDep, db: SessionDep):
    return templates.TemplateResponse(
        request=request,
        name="ai_chat.html",
        context={"user": user}
    )


@router.post("/app/ai-chat/message")
async def ai_chat_message(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    message: str = Form()
):
    now = datetime.now()
    expense_service = ExpenseService(ExpenseRepository(db))
    income_service = IncomeService(IncomeRepository(db))
    sub_service = SubscriptionService(SubscriptionRepository(db))

    total_expenses = expense_service.get_monthly_total(user.id, now.month, now.year)
    total_income = income_service.get_monthly_total(user.id, now.month, now.year)
    total_subs = sub_service.get_monthly_total(user.id)
    remaining = total_income - total_expenses - total_subs

    system_prompt = f"""You are Byte The Budget, a friendly personal finance assistant built into the Byte The Budget app.
The user's current financial summary for {now.strftime("%B %Y")}:
- Total Income: ${total_income:.2f}
- Total Expenses: ${total_expenses:.2f}
- Total Subscriptions: ${total_subs:.2f}
- Remaining Balance: ${remaining:.2f}
Give short, practical financial advice. Be friendly and concise. Keep responses under 3 sentences."""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {get_settings().groq_api_key}"},
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    "max_tokens": 300
                },
                timeout=30.0
            )
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
    except Exception as e:
        reply = "Sorry, I'm having trouble connecting right now. Please try again."

    return JSONResponse({"reply": reply})