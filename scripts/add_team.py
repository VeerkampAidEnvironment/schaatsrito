import click
from flask.cli import with_appcontext
from app import db
from app.models import Rider


@click.command("add-team")
@click.argument("rider_id", type=int)
@click.argument("name", type=str)
@click.argument("country_code", type=str)
@click.argument("gender", type=str)
@with_appcontext
def add_team(rider_id, name, country_code, gender):
    """
    Add a team (country) as a Rider with a specific ID.

    Example:
    flask add-team 2001 "Netherlands" NED women
    """

    # Check if ID already exists
    if Rider.query.get(rider_id):
        click.echo(f"❌ Rider ID {rider_id} already exists.")
        return


    team = Rider(
        id=rider_id,  # 👈 manually set ID
        name=name,
        country=country_code.upper(),
        profile="Team",
        gender=gender.lower()
    )

    db.session.add(team)
    db.session.commit()

    click.echo(f"✅ Team '{name}' added with ID {rider_id}.")
