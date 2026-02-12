import click
from flask.cli import with_appcontext
from app import db
from app.models import Event, Rider, EventStartlistProvisional


@click.command("add-provisional-bulk")
@click.argument("event_id", type=int)
@click.argument("rider_ids", type=str)
@click.option(
    "--clear",
    is_flag=True,
    help="Clear existing provisional startlist before adding new riders."
)
@with_appcontext
def add_provisional_bulk(event_id, rider_ids, clear):
    """
    Add multiple riders to an event's provisional startlist.

    Example:
    flask add-provisional-bulk 5 8000,8001,8002

    With clearing existing:
    flask add-provisional-bulk 5 8000,8001,8002 --clear
    """

    event = Event.query.get(event_id)
    if not event:
        click.echo(f"❌ Event {event_id} not found.")
        return

    # Clear existing if requested
    if clear:
        deleted = EventStartlistProvisional.query.filter_by(
            event_id=event_id
        ).delete()
        click.echo(f"🗑 Cleared {deleted} existing provisional entries.")

    # Parse IDs
    try:
        ids = [int(r.strip()) for r in rider_ids.split(",") if r.strip()]
    except ValueError:
        click.echo("❌ Rider IDs must be comma-separated integers.")
        return

    added = 0
    skipped = 0

    for rider_id in ids:
        rider = Rider.query.get(rider_id)
        if not rider:
            click.echo(f"⚠️ Rider {rider_id} not found. Skipping.")
            skipped += 1
            continue

        exists = EventStartlistProvisional.query.filter_by(
            event_id=event_id,
            rider_id=rider_id
        ).first()

        if exists:
            click.echo(f"⚠️ Rider {rider_id} already in provisional list.")
            skipped += 1
            continue

        db.session.add(EventStartlistProvisional(
            event_id=event_id,
            rider_id=rider_id
        ))

        added += 1

    db.session.commit()

    click.echo("✅ Done.")
    click.echo(f"Added: {added}")
    click.echo(f"Skipped: {skipped}")
