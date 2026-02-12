import click
from datetime import datetime
from flask.cli import with_appcontext
from app import db
from app.models import Event


@click.command("change-start-time")
@click.argument("event_id", type=int)
@click.argument("new_start_time", type=str)
@with_appcontext
def change_start_time(event_id, new_start_time):
    """
    Change the start time of an event.

    Example:
    flask change-start-time 5 "2026-02-17 14:30:00"
    """

    try:
        # Parse datetime string
        new_dt = datetime.strptime(new_start_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        click.echo("❌ Invalid datetime format. Use: YYYY-MM-DD HH:MM:SS")
        return

    event = Event.query.get(event_id)

    if not event:
        click.echo(f"❌ Event with ID {event_id} not found.")
        return

    old_time = event.start_datetime
    event.start_datetime = new_dt

    db.session.commit()

    click.echo(f"✅ Event '{event.name}' updated.")
    click.echo(f"Old start time: {old_time}")
    click.echo(f"New start time: {event.start_datetime}")
