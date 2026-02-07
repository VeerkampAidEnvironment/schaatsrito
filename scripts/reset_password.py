import click
from app import db
from app.models import User

@click.command("reset-password")
@click.argument("username")
@click.password_option(
    confirmation_prompt=True,
    help="New password for the user"
)
def reset_password(username, password):
    """Reset a user's password"""

    user = User.query.filter_by(username=username).first()

    if not user:
        click.echo(f"❌ User '{username}' not found")
        return

    user.set_password(password)
    db.session.commit()

    click.echo(f"✅ Password reset for user '{username}'")
