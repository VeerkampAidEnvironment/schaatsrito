import click
from flask.cli import with_appcontext
from app import db
from app.models import Event, Rider, EventStartlist


@click.command("startlist")
@click.argument("action", type=click.Choice(["add", "remove"]))
@click.argument("event_id", type=int)
@click.argument("rider_id", type=int)
@with_appcontext
def manage_startlist(action, event_id, rider_id):
    """
    Add or remove a rider from the REAL startlist.

    Examples:

    Add:
    flask startlist add 5 8000

    Remove:
    flask startlist remove 5 8000
    """

    event = Event.query.get(event_id)
    if not event:
        click.echo(f"❌ Event {event_id} not found.")
        return

    rider = Rider.query.get(rider_id)
    if not rider:
        click.echo(f"❌ Rider {rider_id} not found.")
        return

    entry = EventStartlist.query.filter_by(
        event_id=event_id,
        rider_id=rider_id
    ).first()

    if action == "add":
        if entry:
            click.echo("⚠️ Rider already in startlist.")
            return

        new_entry = EventStartlist(
            event_id=event_id,
            rider_id=rider_id
        )
        db.session.add(new_entry)
        db.session.commit()

        click.echo(f"✅ Added {rider.name} to startlist for {event.name}.")

    elif action == "remove":
        if not entry:
            click.echo("⚠️ Rider not in startlist.")
            return

        db.session.delete(entry)
        db.session.commit()

        click.echo(f"🗑 Removed {rider.name} from startlist for {event.name}.")
