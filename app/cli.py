import typer
from sqlmodel import Session

app = typer.Typer()


def get_session():
    from app.database import get_cli_session
    return get_cli_session()


@app.command("init")
def init_db():
    """Create all tables and seed default data."""
    from app.database import create_db_and_tables
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
    typer.echo("Tables created.")

    with get_session() as session:
        # seed admin accounts
        admin_accounts = [
            {"username": "bob", "password": "bobpass", "email": "bob@bytethebyte.com"},
        ]
        for account in admin_accounts:
            existing = session.exec(select(User).where(User.username == account["username"])).first()
            if not existing:
                user = User(
                    username=account["username"],
                    email=account["email"],
                    password=encrypt_password(account["password"]),
                    role="admin"
                )
                session.add(user)
                typer.echo(f"Admin user '{account['username']}' created.")
            else:
                typer.echo(f"Admin user '{account['username']}' already exists, skipping.")

        session.commit()

        # get bob's id
        bob = session.exec(select(User).where(User.username == "bob")).first()

        # seed default categories
        default_categories = [
            "Food", "Transport", "Entertainment", "Rent",
            "Education", "Health", "Utilities", "Clothing",
            "Savings", "Other"
        ]
        for name in default_categories:
            existing = session.exec(select(Category).where(Category.name == name)).first()
            if not existing:
                session.add(Category(name=name, is_default=True))
                typer.echo(f"Category '{name}' created.")

        session.commit()

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
                typer.echo(f"Subscription template '{t['name']}' created.")

        session.commit()

        # ── BOB'S SEED DATA ──────────────────────────────────────────────────

        # helper to get category id by name
        def cat_id(name):
            return session.exec(select(Category).where(Category.name == name)).first().id

        # INCOME
        bob_income = [
            {"source": "Monthly Allowance", "amount": 3800.00, "type": "Allowance",      "date_received": date(2025, 4, 1)},
            {"source": "Part-Time Job",      "amount": 2400.00, "type": "Employment",     "date_received": date(2025, 4, 1)},
            {"source": "Monthly Allowance", "amount": 3800.00, "type": "Allowance",      "date_received": date(2025, 3, 1)},
            {"source": "Part-Time Job",      "amount": 2400.00, "type": "Employment",     "date_received": date(2025, 3, 1)},
            {"source": "Monthly Allowance", "amount": 3800.00, "type": "Allowance",      "date_received": date(2025, 2, 1)},
            {"source": "Freelance Work",     "amount": 1500.00, "type": "Freelance",      "date_received": date(2025, 2, 14)},
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
        typer.echo("Bob's income seeded.")

        # EXPENSES
        bob_expenses = [
            # April
            {"description": "Subway Sandwich",  "amount": 45.00,  "date": date(2025, 4, 10), "category": "Food",          "notes": None},
            {"description": "Maxi Taxi",         "amount": 8.00,   "date": date(2025, 4, 11), "category": "Transport",     "notes": None},
            {"description": "Movie Tickets",     "amount": 160.00, "date": date(2025, 4, 8),  "category": "Entertainment", "notes": "Cinema with friends"},
            {"description": "Textbooks",         "amount": 340.00, "date": date(2025, 4, 5),  "category": "Education",     "notes": None},
            {"description": "Groceries",         "amount": 220.00, "date": date(2025, 4, 3),  "category": "Food",          "notes": None},
            {"description": "Rent",              "amount": 2500.00,"date": date(2025, 4, 1),  "category": "Rent",          "notes": "April rent"},
            # March
            {"description": "KFC",               "amount": 85.00,  "date": date(2025, 3, 22), "category": "Food",          "notes": None},
            {"description": "Gas",               "amount": 120.00, "date": date(2025, 3, 18), "category": "Transport",     "notes": None},
            {"description": "Concert Tickets",   "amount": 250.00, "date": date(2025, 3, 15), "category": "Entertainment", "notes": None},
            {"description": "Rent",              "amount": 2500.00,"date": date(2025, 3, 1),  "category": "Rent",          "notes": "March rent"},
            {"description": "Pharmacy",          "amount": 75.00,  "date": date(2025, 3, 10), "category": "Health",        "notes": None},
            # February
            {"description": "Groceries",         "amount": 195.00, "date": date(2025, 2, 20), "category": "Food",          "notes": None},
            {"description": "Uber",              "amount": 55.00,  "date": date(2025, 2, 17), "category": "Transport",     "notes": None},
            {"description": "Rent",              "amount": 2500.00,"date": date(2025, 2, 1),  "category": "Rent",          "notes": "February rent"},
            {"description": "New Sneakers",      "amount": 380.00, "date": date(2025, 2, 12), "category": "Clothing",      "notes": None},
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
        typer.echo("Bob's expenses seeded.")

        # BUDGETS (one per relevant category)
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
        typer.echo("Bob's budgets seeded.")

        # SUBSCRIPTIONS
        bob_subscriptions = [
            {"name": "Netflix",          "amount": 65.00,  "billing_cycle": "monthly", "next_renewal": date(2025, 5, 1)},
            {"name": "Spotify",          "amount": 20.00,  "billing_cycle": "monthly", "next_renewal": date(2025, 5, 1)},
            {"name": "Flow WiFi",        "amount": 200.00, "billing_cycle": "monthly", "next_renewal": date(2025, 5, 2)},
            {"name": "Adobe CC",         "amount": 80.00,  "billing_cycle": "monthly", "next_renewal": date(2025, 5, 10)},
            {"name": "YouTube Premium",  "amount": 30.00,  "billing_cycle": "monthly", "next_renewal": date(2025, 5, 15)},
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
        typer.echo("Bob's subscriptions seeded.")

        session.commit()

    typer.echo("Database initialised successfully.")


@app.command("drop")
def drop_db():
    """Drop all tables. WARNING: deletes all data."""
    confirm = typer.confirm("This will delete ALL data. Are you sure?")
    if not confirm:
        typer.echo("Aborted.")
        raise typer.Exit()
    from sqlmodel import SQLModel
    from app.database import engine
    import app.models  # ensures all models are registered
    SQLModel.metadata.drop_all(engine)
    typer.echo("All tables dropped.")


@app.command("create-admin")
def create_admin(
    username: str = typer.Option(..., prompt=True),
    email: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True, hide_input=True)
):
    """Create a new admin user interactively."""
    from app.models.user import User
    from app.utilities.security import encrypt_password
    from sqlmodel import select

    with get_session() as session:
        existing = session.exec(select(User).where(User.username == username)).first()
        if existing:
            typer.echo(f"User '{username}' already exists.")
            raise typer.Exit()
        user = User(
            username=username,
            email=email,
            password=encrypt_password(password),
            role="admin"
        )
        session.add(user)
        session.commit()
        typer.echo(f"Admin user '{username}' created successfully.")


@app.command("list-users")
def list_users():
    """List all registered users."""
    from app.models.user import User
    from sqlmodel import select

    with get_session() as session:
        users = session.exec(select(User)).all()
        if not users:
            typer.echo("No users found.")
            return
        typer.echo(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Role':<15} {'Active'}")
        typer.echo("-" * 75)
        for u in users:
            typer.echo(f"{u.id:<5} {u.username:<20} {u.email:<30} {u.role:<15} {u.is_active}")


@app.command("reset")
def reset_db():
    """Drop all tables then reinitialise with default data."""
    confirm = typer.confirm("This will delete ALL data and reseed. Are you sure?")
    if not confirm:
        typer.echo("Aborted.")
        raise typer.Exit()
    from sqlmodel import SQLModel
    from app.database import engine
    import app.models
    SQLModel.metadata.drop_all(engine)
    typer.echo("Tables dropped.")
    init_db()


if __name__ == "__main__":
    app()