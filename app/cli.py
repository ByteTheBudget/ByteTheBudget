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
    from app.utilities.security import encrypt_password
    from sqlmodel import select

    create_db_and_tables()
    typer.echo("Tables created.")

    with get_session() as session:
        # seed admin accounts
        admin_accounts = [
            {"username": "bob", "password": "bobpass", "email": "bob@bytethebyte.com"},
            # add your dev accounts here
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
    drop_db.__wrapped__() if hasattr(drop_db, '__wrapped__') else None
    from sqlmodel import SQLModel
    from app.database import engine
    import app.models
    SQLModel.metadata.drop_all(engine)
    typer.echo("Tables dropped.")
    init_db()


if __name__ == "__main__":
    app()