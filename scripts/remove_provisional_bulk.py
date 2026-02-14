import click
from flask.cli import with_appcontext
from app import db
from app.models import Event, EventStartlistProvisional


@click.command("remove-provisional-bulk")
@click.argument("event_id", type=int)
@click.argument("rider_ids", type=str)
@with_appcontext
def remove_provisional_bulk(event_id, rider_ids):
    """
    Remove multiple riders from provisional startlist.

    Example:
    flask remove-provisional-bulk 5 8000,8001,8002
    """

    event = Event.query.get(event_id)
    if not event:
        click.echo(f"❌ Event {event_id} not found.")
        return

    try:
        ids = [int(r.strip()) for r in rider_ids.split(",") if r.strip()]
    except ValueError:
        click.echo("❌ Rider IDs must be comma-separated integers.")
        return

    removed = 0
    skipped = 0

    for rider_id in ids:
        entry = EventStartlistProvisional.query.filter_by(
            event_id=event_id,
            rider_id=rider_id
        ).first()

        if entry:
            db.session.delete(entry)
            removed += 1
        else:
            skipped += 1

    db.session.commit()

    click.echo("✅ Done.")
    click.echo(f"Removed: {removed}")
    click.echo(f"Not found in provisional: {skipped}")
